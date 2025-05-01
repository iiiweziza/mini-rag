from pydantic-settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str 
    APP_VERSION: str
    API_KEY: str 

    class Config:
        env_file = "env"

def get_settings():
    return Settings()     