from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    API_KEY: str
    FILE_ALLOWED_TYPE: List[str]
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE: int
     
    
    POSTGRES_USERNAME=str
    POSTGRES_PASSWORD=str
    POSTGRES_HOST=str
    POSTGRES_PORT=int
    POSTGRES_MAIN_DATABASE=str

        

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    GENERATION_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_SIZE: Optional[int] = None

    DEFAULT_INPUT_MAX_TOKENS: Optional[int] = None
    DEFAULT_OUTPUT_MAX_TOKENS: Optional[int] = None
    DEFAULT_TEMPERATURE: Optional[float] = None

    VECTOR_DB_BACKEND: Optional[str] = None
    VECTOR_DB_PATH: Optional[str] = None
    VECTOR_DB_DISTANCE_METHOD: Optional[str] = None  # Options: "EUCLIDEAN", "COSINE", "DOT"

    DEFAULT_LANGUAGE: str = "en"  # Default language for templates
    PRIMARY_LANGUAGE: str = "en"  # Primary language for templates

    model_config = SettingsConfigDict(env_file=".env")

def get_settings():
    return Settings()