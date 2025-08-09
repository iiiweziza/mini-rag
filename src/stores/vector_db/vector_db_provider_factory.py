from .providers import QdrantDBProvider
from .vector_db_enums import DistanceMethodEnums, VectorDBEnums
from controllers.base_controller import BaseController

class VectorDBProviderFactory:
    def __init__(self,config):
        self.config = config 
        self.base_controller = BaseController() 

    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            print(f"Initializing vector database at path: {db_path}")
            
            if not self.config.VECTOR_DB_PATH:
                raise ValueError("VECTOR_DB_PATH is not configured in settings")

            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD 
            )
        raise ValueError(f"Unknown vector database provider: {provider}")
