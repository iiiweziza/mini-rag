from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings  # importing settings from helpers file
import os 

# APIRoute => to help you routing between APIs in the system and call it from another file.
base_router = APIRouter(  

    prefix='/api/v1',          # you should write the prefix before any call page "host name" to run
    tags = ['/api/v1']           # can put related things in tags 
)

@base_router.get("/")
async def welcome(app_settings :Settings  = Depends(get_settings)):  #:Settings => from type Settings
    # Depends make it is can't be called without the settings file
    # get_settings function is used to get the settings from the config file
    app_name = app_settings.APP_NAME  
    app_version = app_settings.APP_VERSION  # importing from get_settings function
    return{
        "message":"Welcome to Mini RAG App!",
        "App Name: " : app_name,
        "App Version: ": app_version

    }  # now you can call base_router from main.py