from fastapi import FastAPI 
from helpers.config import get_settings
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from .stores.llm.llm_provider_factory import LLMProviderFactory

app = FastAPI()

#Testing Events: startup - shutdown

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

    llm_provider_factory = LLMProviderFactory(config=app_settings)
    # generation client for LLM providers
    app.generation_client = llm_provider_factory.create(provider=app_settings.GENERATION_BACKEND)
    app.generation_client.set_generate_model(model_name = app_settings.GENERATION_MODEL_ID)  # here we can set any model 
    
    ### may be change model id method later 

    # embedding client for LLM providers
    app.embedding_client = llm_provider_factory.create(provider=app_settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embeddings_model(model_name = app_settings.EMBEDDING_MODEL_ID,embedding_size = app_settings.EMBEDDING_MODEL_SIZE)


async def shutdown_event():
    # Close the MongoDB connection when the app is shutting down
    app.mongo_connection.close()

app.router.lifespan.on_startup.append(startup_event)
app.router.lifespan.on_shutdown.append(shutdown_event)

# Include routers for your API endpoints
app.include_router(base.base_router)
app.include_router(data.data_router)