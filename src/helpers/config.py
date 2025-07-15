from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str 
    APP_VERSION: str
    API_KEY: str 
    FILE_ALLOWED_TYPE: list
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE : int
    MONGO_URI: str
    MONGODB_DATA_BASE: str

    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str

    OPENAI_API_KEY: str =None
    OPENAI_API_URL : str =None
    COHERE_API_KEY : str =None

    GENERATION_MODEL_ID : str =None
    EMBEDDING_MODEL_ID : str =None
    EMBEDDING_MODEL_SIZE : int =None

    DEFAULT_INPUT_MAX_CHARACTERS : int =None
    DEFAULT_OUTPUT_MAX_CHARACTERS : int =None
    DEFAULT_TEMPERATURE : float =None

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()     