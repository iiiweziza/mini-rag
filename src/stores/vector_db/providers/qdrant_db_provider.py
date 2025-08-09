from qdrant_client import QdrantClient, models
from ..vector_db_interface import VectorDBInterface
from ..vector_db_enums import  DistanceMethodEnums
import logging
from typing import List

class QdrantDBProvider(VectorDBInterface):
    def __init__(self,db_path: str, distance_method:str):
        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.EUCLIDEAN.value:
            self.distance_method = models.Distance.EUCLIDEAN
        elif distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        


        self.logger = logging.getLogger(__name__)
  

    def connect(self):
        """Connect to the vector database."""
        self.client = QdrantClient(path=self.db_path)
    
    def disconnect(self):
        """Disconnect from the vector database."""
        self.client = None

    def is_collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists in the vector database."""
        try:
            # New way to check collection existence
            self.client.get_collection(collection_name)
            return True
        except Exception:
            return False

    def list_all_collections(self) -> List:
        """List all collections in the vector database."""
        return self.client.get_collections().collections

    def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a specific collection."""
        try:
            return self.client.get_collection(collection_name)
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            return None

    def delete_collection(self, collection_name: str):
        """Delete a specific collection from the vector database."""
        try:
            return self.client.delete_collection(collection_name)
        except Exception as e:
            self.logger.warning(f"Error deleting collection '{collection_name}': {str(e)}")
            return None

    def create_collection(self, collection_name: str, embedding_size: int,
                           do_reset: bool = False):
        """Create a new collection in the vector database."""
        try:
            if do_reset:
                self.delete_collection(collection_name)

            if not self.is_collection_exists(collection_name):
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=embedding_size,
                        distance=self.distance_method
                    )
                )
            return True
        except Exception as e:
            self.logger.error(f"Error in create_collection: {str(e)}")
            return False

    def insert_one_vector(self, collection_name: str, text: str, vector: list,
                          metadata: dict = None,
                          record_id: str = None):
        """Insert a single vector into the specified collection."""
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection '{collection_name}' does not exist.")
            return False
        
        try:
            _ = self.client.upload_points(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                            id=record_id,
                            vector=vector,
                            payload={
                                "text": text,
                                "metadata": metadata or {}
                            }
                        )
                    ]
                )
        except Exception as e:
            self.logger.error(f"Error inserting vector into collection '{collection_name}': {e}")
            return False
        return True
    
    def insert_many_vectors(self, collection_name: str, texts: list, vectors: list,
                            metadata: list = None,
                            record_ids: list = None, batch_size: int = 50
                            ):
        """Insert multiple vectors into the specified collection."""
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        self.logger.info(f"Preparing to insert {len(texts)} vectors into {collection_name}")

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            points = [
                models.PointStruct(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x] or {}
                    }
                )
                for x in range(len(batch_texts))
            ]
            
            try:
                self.client.upload_points(
                    collection_name=collection_name,
                    points=points
                )
                self.logger.info(f"Successfully inserted batch {i//batch_size + 1}")
            except Exception as e:
                self.logger.error(f"Error inserting batch into collection '{collection_name}': {e}")
                return False

        return True

    def search_by_vector(self, collection_name: str, vector: list,
                            limit: int = 10):
        """Search for vectors in the specified collection using a vector."""
        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )


