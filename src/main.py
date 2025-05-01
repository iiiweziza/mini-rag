from fastapi import FastAPI 
from dotenv import load_dotenv   # for can load from .env file to the system
load_dotenv(".env")
from routes import base



app = FastAPI()
#call base_router by app
app.include_router(base.base_router)