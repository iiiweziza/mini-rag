from .base_controller import BaseController
from models.db_schemes import Project 
from models.db_schemes import DataChunk
from stores.llm.llm_enums import EmbedDocumentTypeEnums
from typing import List 
import json 

class NLPController(BaseController):
    def __init__(self, vector_db_client, embedding_client, generation_client,parser_template):
        super().__init__()
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.parser_template = parser_template

    def create_collection_name(self, project_id: str):
        return f"project_{project_id}_collection".strip()

    def reset_vector_db_collection(self, project: Project ):
        collection_name = self.create_collection_name(project.project_id)
        self.vector_db_client.delete_collection(collection_name = collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info = self.vector_db_client.get_collection_info(collection_name=collection_name)

        return json.loads(
                json.dumps(collection_info, default =lambda o: o.__dict__)
        )
    
    def check_llm_configuration(self):
        """Check if LLM is properly configured and working"""
        messages = []
        try:
            # Test the embedding model with a simple text
            test_text = "This is a test text to verify embedding functionality."
            messages.append("Testing LLM configuration...")
            
            if not self.embedding_client:
                messages.append("Error: Embedding client is not initialized")
                return False, messages
                
            if not hasattr(self.embedding_client, 'embedding_size'):
                messages.append("Error: Embedding model size not configured")
                return False, messages
                
            messages.append(f"Embedding model size: {self.embedding_client.embedding_size}")
            
            # Try to generate a test embedding
            test_vector = self.embedding_client.embed_text(
                text=test_text,
                document_type="document"
            )
            
            if test_vector is None:
                messages.append("Error: Failed to generate test embedding")
                return False, messages
                
            vector_size = len(test_vector)
            messages.append(f"Test embedding generated successfully. Vector size: {vector_size}")
            
            if vector_size != self.embedding_client.embedding_size:
                messages.append(f"Warning: Embedding size mismatch. Expected: {self.embedding_client.embedding_size}, Got: {vector_size}")
                return False, messages
                
            return True, messages
            
        except Exception as e:
            messages.append(f"Error testing LLM configuration: {str(e)}")
            return False, messages

    def indexes_into_vector_db(self, project: Project, chunks: List[DataChunk],
                               chunk_ids: List[int],
                               do_reset: bool = False):
        messages = []  # List to collect debug messages
        try:
            # First check LLM configuration
            llm_ok, llm_messages = self.check_llm_configuration()
            messages.extend(llm_messages)
            
            if not llm_ok:
                messages.append("LLM configuration check failed - aborting indexing")
                return False, messages
            
            # get collection name
            collection_name = self.create_collection_name(project.project_id)
            messages.append(f"Created collection name: {collection_name}")

            # manage and convert items
            texts = [t.chunk_text for t in chunks]
            metadata = [t.chunk_metadata for t in chunks]
            messages.append(f"Processing {len(texts)} text chunks")
            if texts:
                messages.append(f"Sample text: {texts[0][:100]}")
                messages.append(f"Sample metadata: {metadata[0]}")

            # Generate embeddings one by one to catch errors
            vectors = []
            for i, text in enumerate(texts):
                try:
                    vector = self.embedding_client.embed_text(
                        text=text,
                        document_type=EmbedDocumentTypeEnums.DOCUMENT.value
                    )
                    if vector is None:
                        messages.append(f"Warning: Got None vector for chunk {i}")
                        continue
                    vectors.append(vector)
                except Exception as e:
                    messages.append(f"Error embedding chunk {i}: {str(e)}")
                    continue

            if not vectors:
                messages.append("Error: No vectors were generated")
                return False, messages

            messages.append(f"Successfully generated {len(vectors)} embeddings")
            if vectors:
                messages.append(f"First vector dimension: {len(vectors[0])}")

            # create collection if not exists
            try:
                result = self.vector_db_client.create_collection(
                    collection_name=collection_name,
                    embedding_size=self.embedding_client.embedding_size,
                    do_reset=do_reset
                )
                messages.append(f"Collection creation/reset result: {result}")
            except Exception as e:
                messages.append(f"Error creating/resetting collection: {str(e)}")
                return False, messages

            # insert into DB
            try:
                if not vectors or len(vectors) == 0:
                    messages.append("No vectors to insert")
                    return False, messages

                if len(texts) != len(vectors):
                    messages.append(f"Mismatch between texts ({len(texts)}) and vectors ({len(vectors)})")
                
                messages.append(f"Attempting to insert {len(vectors)} vectors into collection {collection_name}")
                
                success = self.vector_db_client.insert_many_vectors(
                    collection_name=collection_name,
                    texts=texts[:len(vectors)],
                    vectors=vectors,
                    metadata=metadata[:len(vectors)],
                    record_ids=chunk_ids[:len(vectors)]
                )
                
                if success:
                    messages.append(f"Successfully inserted {len(vectors)} vectors into collection {collection_name}")
                else:
                    messages.append("Vector DB insertion failed")
                return success, messages
            except Exception as e:
                messages.append(f"Error inserting vectors: {str(e)}")
                return False, messages

        except Exception as e:
            messages.append(f"Unexpected error in indexes_into_vector_db: {str(e)}")
            return False, messages


    def search_vector_db_collection(self, project: Project ,text: str, limit: int = 5):
        """
        Search the vector database collection for the given project using the provided text.
        Returns a list of matching DataChunk objects.
        """
        collection_name = self.create_collection_name(project.project_id)

        # Generate embedding for the search text
        vector = self.embedding_client.embed_text(
            text=text,
            document_type=EmbedDocumentTypeEnums.QUERY.value
        )
        if vector is None or len(vector) == 0:
            raise ValueError("Failed to generate embedding for the search text")
        
        # do semantic search 
        search_results = self.vector_db_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )
        if not search_results:
            raise ValueError("No search results found for the given vector")
        return search_results
    
    def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt
        system_prompt = self.parser_template.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.parser_template.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.parser_template.get("rag", "footer_prompt")

        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.abstract_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        # step4: Retrieve the Answer
        try:
            response = self.generation_client.generate_text(
                prompt=full_prompt,
                chat_history=chat_history
            )
            # Handle the response object appropriately
            answer = response.text if hasattr(response, 'text') else str(response)
            
            # Add the user's question and the answer to chat history
            chat_history.extend([
                {
                    "role": self.generation_client.enums.USER.value,
                    "content": query
                },
                {
                    "role": self.generation_client.enums.ASSISTANT.value,
                    "content": answer
                }
            ])
        except Exception as e:
            # Log the error and return None
            print(f"Error generating response: {str(e)}")
            answer = None

        return answer, full_prompt, chat_history
    