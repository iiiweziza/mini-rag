from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str 
    APP_VERSION: str
    API_KEY: str 
    FILE_ALLOWED_TYPE: list
    FILE_MAX_SIZE: int
    FILE_CHUNK_SIZE : int

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()     