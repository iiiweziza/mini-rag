from fastapi import FastAPI, APIRouter
import os 

# APIRoute => to help you routing between APIs in the system and call it from another file.
base_router = APIRouter(  

    prefix='/api/v1',          # you should write the prefix before any call page "host name" to run
    tags = ['/api/v1']           # can put related things in tags 
)

@base_router.get("/")
async def welcome():
    app_name = os.getenv('APP_NAME')   # importing from .env file
    app_version = os.getenv('APP_VERSION')
    return{
        "message":"Welcome to Mini RAG App!",
        "App Name: " : app_name,
        "App Version: ": app_version

    }  # now you can call base_router from main.py