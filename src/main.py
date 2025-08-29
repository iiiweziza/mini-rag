from fastapi import FastAPI 
from helpers.config import get_settings
from routes import base, data , nlp
from motor.motor_asyncio import AsyncIOMotorClient
from stores.llm.llm_provider_factory import LLMProviderFactory
from stores.vector_db.vector_db_provider_factory import VectorDBProviderFactory
from stores.llm.llm_enums import EmbedDocumentTypeEnums
from stores.llm.templates.parser_template import TemplateParser

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
    vector_db_provider_factory = VectorDBProviderFactory(config=app_settings)
    # generation client for LLM providers
    app.generation_client = llm_provider_factory.create(provider=app_settings.GENERATION_BACKEND)
    app.generation_client.set_generate_model(model_name = app_settings.GENERATION_MODEL_ID)  # here we can set any model 
    
    ### may be change model id method later 

    # embedding client for LLM providers
    try:
        print("Initializing embedding client...")
        app.embedding_client = llm_provider_factory.create(provider=app_settings.EMBEDDING_BACKEND)
        
        print(f"Setting up embedding model: {app_settings.EMBEDDING_MODEL_ID}, size: {app_settings.EMBEDDING_MODEL_SIZE}")
        app.embedding_client.set_embeddings_model(
            model_name=app_settings.EMBEDDING_MODEL_ID, 
            embedding_size=app_settings.EMBEDDING_MODEL_SIZE
        )

        # Verify embedding functionality
        print("Testing embedding generation...")
        test_text = "This is a test text for embedding verification."
        test_embedding = app.embedding_client.embed_text(
            text=test_text,
            document_type=EmbedDocumentTypeEnums.DOCUMENT.value
        )
        
        if test_embedding is None:
            raise ValueError("Test embedding generation failed - returned None")
            
        actual_size = len(test_embedding)
        if actual_size != app_settings.EMBEDDING_MODEL_SIZE:
            raise ValueError(f"Embedding size mismatch. Expected: {app_settings.EMBEDDING_MODEL_SIZE}, Got: {actual_size}")
            
        print(f"Embedding test successful! Vector size: {actual_size}")
        
    except Exception as e:
        print(f"ERROR: Failed to initialize embedding client: {str(e)}")
        print("WARNING: Application may not function correctly without working embeddings")
        # You might want to prevent startup if embeddings are critical:
        # raise e

    # vector database client    
    app.vector_db_client = vector_db_provider_factory.create(provider=app_settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()   

    app.parser_template = TemplateParser(
        language=app_settings.PRIMARY_LANGUAGE,
        default_language=app_settings.DEFAULT_LANGUAGE
        )


async def shutdown_event():
    # Close the MongoDB connection when the app is shutting down
    app.mongo_connection.close()
    app.vector_db_client.disconnect()


app.on_event("startup")(startup_event)
app.on_event("shutdown")(shutdown_event)

# Include routers for your API endpoints
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)