from fastapi import FastAPI 
from helpers.config import get_settings
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

#Testing Events: startup - shutdown
@app.on_event("startup")
async def startup_event():
    """
    Event to be called when the app starts
    """
    app_settings = get_settings()
    # Create an asynchronous MongoDB client using the connection URL from settings 
    # when the app starts up, the mongo connection will be created
    # Then we create and connect client_db by the connection URL and database name from this connection 
    app.mongo_connection = AsyncIOMotorClient(app_settings.MONGO_URI)
    app.client_db = app.mongo_connection[app_settings.MONGODB_DATA_BASE]

@app.on_event("shutdown")
async def shutdown_event():
    # Close the MongoDB connection when the app is shutting down
    app.mongo_connection.close()

# Include routers for your API endpoints
app.include_router(base.base_router)
app.include_router(data.data_router)