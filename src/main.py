from fastapi import FastAPI 
#from helpers import get_settings
from routes import base, data



app = FastAPI()
#call base_router by app
app.include_router(base.base_router)
app.include_router(data.data_router)