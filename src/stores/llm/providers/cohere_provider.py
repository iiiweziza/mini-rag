from ..llm_interface import LLMInterface
from ..llm_enums import CohereEnums, EmbedDocumentTypeEnums
import cohere
import logging

class CohereProvider(LLMInterface):
    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1024,
                 default_output_max_tokens: int = 1024,
                 default_temperature: float = 0.7,
                 ):
            
            self.api_key = api_key 
    
            self.default_input_max_characters = default_input_max_characters
            self.default_output_max_tokens = default_output_max_tokens
            self.default_temperature = default_temperature

            self.generation_model_id = None
            self.embeddings_model_id = None
            self.embedding_size = None


            self.client = cohere.ClientV2(
                api_key=self.api_key,   
            )

            self.logger = logging.getLogger(__name__)

        # Functions to set models and parameters
    def process_text(self, text: str):
        """
        Process the input text to ensure it meets the requirements for OpenAI.
        This can include truncating or formatting the text as needed.
        """
        return text[:self.default_input_max_characters].strip()  # Truncate to max characters and strip whitespace
    
    
    def set_generate_model(self, model_name: str):
        self.generation_model_id = model_name

    def set_embeddings_model(self, model_name: str, embedding_size: int):
        self.embeddings_model_id = model_name
        self.embedding_size = embedding_size 

    def generate_text(self, prompt: str, chat_history: list = [],
                        max_output_tokens: int = None, temperature: float = None):
            # Implementation for generating text using Cohere API

        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model is not set.")
            return None
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_output_max_tokens
        temperature = temperature if temperature else self.default_temperature

        chat_history.append(
            self.abstract_prompt(prompt = prompt, role=CohereEnums.USER.value)
        )

        response = self.client.chat(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
            )

        if not response or not response.message or len(response.message) == 0:
            self.logger.error("No response from Cohere, error while generating text.")
            return None

        return response.message.content[0].text

        
            
    def embed_text(self, text: str, document_type: str= None):
            # Implementation for embedding text using Cohere API
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        if not self.embeddings_model_id:
            self.logger.error("Embeddings model for Cohere is not set.")
            return None
            
        input_type = CohereEnums.DOCUMENT.value
        if document_type is EmbedDocumentTypeEnums.QUERY.value:
            input_type = CohereEnums.QUERY.value

        response = self.client.embed(
                model=self.embeddings_model_id,
                texts=[self.process_text(text)],
                input_type=input_type,
                embedding_types = ['float']  #default embedding type
            )

        if not response or not response.embeddings or len(response.embeddings.float) == 0:
            self.logger.error("Error while embedding text.")
            return None
        return response.embeddings.float[0]  # Assuming the first embedding is the one we want
        
    def abstract_prompt(self, prompt: str, role: str):    # used it in generation text 
        # Implementation for abstracting prompt using Cohere API
        return {
                "role": role,
                "content": self.process_text(prompt)
            }
        # Add any additional methods or properties as needed    
        
        


        
