from abc import ABC, abstractmethod
from typing import List
from models.db_schemes.data_chunk import RetrievedDocument

class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        """Connect to the vector database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the vector database."""
        pass

    @abstractmethod
    def is_collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists in the vector database."""
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        """List all collections in the vector database."""
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        """Get information about a specific collection."""
        pass

    @abstractmethod 
    def delete_collection(self, collection_name: str):
        """Delete a specific collection from the vector database."""
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, embedding_size: int,
                           do_reset: bool = False):
        """Create a new collection in the vector database."""
        pass

    @abstractmethod
    def insert_one_vector(self, collection_name: str, text: str, vector: list,
                          metadata: dict = None,
                          record_id: str = None):
        """Insert a single vector into the specified collection."""
        pass

    @abstractmethod
    def insert_many_vectors(self, collection_name: str, texts: list, vectors: list,
                            metadata: list = None,
                            record_ids: list = None, batch_size: int = 50
                            ):
        """Insert multiple vectors into the specified collection."""
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list,
                            limit: int = 10)-> List[RetrievedDocument]: 
        """Search for vectors in the specified collection using a vector."""
        pass