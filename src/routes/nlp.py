from fastapi import FastAPI, APIRouter, status , Request   
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings  # importing settings from helpers file
from routes.schemes.nlp_schema import push_reset , search_request
from models.project_model import ProjectModel 
from models.enums import ResponseEnumSignal
from models.chunk_model import ChunkModel
from controllers.nlp_controller import NLPController

import logging

logs = logging.getLogger('uvicorn.error')


nlp_router = APIRouter(  
    prefix='/api/v1/nlp',          # you should write the prefix before any call page "host name" to run
    tags = ['/api/v1/nlp']           # can put related things in tags
)

@nlp_router.post("/index/push/{Project_id}")
async def index_project(request:Request,Project_id: str,
                      push_request: push_reset ):
    #the request follow the app at startup and can store and gest all the data 
    
    project_model=await ProjectModel.create_instance(
        db_client=request.app.db_client)  # all the models now will treate with the client 
      
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )
    # get the project or create a new one if it doesn't exist with same id
    project = await project_model.get_project_or_create_one(
        project_id = Project_id 
    )

    """ Now I want to send Chunks to converted it to vectorDB , but I will use the controller to do that , 
        NLP controller for nlp processes 
    """
    if not project: 
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": ResponseEnumSignal.PROJECT_NOT_FOUND.value}
        )
    

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        parser_template=request.app.parser_template
    )

    debug_messages = []
    inserted_items_count = 0
    BATCH_SIZE = 100  # Process chunks in batches of 100
    
    debug_messages.append(f"Starting indexing for project {project.id}")
    
    try:
        # Get all chunks at once with a reasonable limit
        # Use project_id (string) instead of MongoDB _id
        all_chunks = await chunk_model.get_project_chunks_bulk(
            project_id=Project_id,  # Use the original project_id string
            limit=1000  # Reasonable limit to prevent memory issues
        )
        total_chunks = len(all_chunks)
        debug_messages.append(f"Retrieved {total_chunks} chunks for processing")
        debug_messages.append(f"Looking for chunks with project_id: {Project_id}")
        
        if total_chunks == 0:
            debug_messages.append("No chunks found for indexing")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "inserted_items_count": 0,
                    "message": ResponseEnumSignal.CHUNKS_INDEXED_SUCCESSFULLY.value,
                    "debug_info": debug_messages
                }
            )
        
        # Process chunks in batches
        for i in range(0, total_chunks, BATCH_SIZE):
            batch = all_chunks[i:i + BATCH_SIZE]
            chunk_ids = list(range(i, i + len(batch)))
            
            debug_messages.append(f"Processing batch {i//BATCH_SIZE + 1} of {(total_chunks + BATCH_SIZE - 1)//BATCH_SIZE}")
            
            is_inserted, indexing_messages = nlp_controller.indexes_into_vector_db(
                project=project,
                chunks=batch,
                do_reset=push_request.do_reset and i == 0,  # Only reset on first batch
                chunk_ids=chunk_ids
            )
            
            if not is_inserted:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "message": ResponseEnumSignal.VECTOR_DB_INSERTION_FAILED.value,
                        "debug_info": debug_messages + indexing_messages
                    }
                )
                
            inserted_items_count += len(batch)
            debug_messages.append(f"Successfully indexed {len(batch)} chunks")
            
    except Exception as e:
        error_msg = f"Error during chunk processing: {str(e)}"
        debug_messages.append(error_msg)
        logs.error(error_msg)

    final_msg = f"Total inserted chunks for project {project.id}: {inserted_items_count}"
    logs.info(final_msg)
    debug_messages.append(final_msg)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "inserted_items_count": inserted_items_count,
            "message": ResponseEnumSignal.CHUNKS_INDEXED_SUCCESSFULLY.value,
            "debug_info": debug_messages
        }
    )


@nlp_router.get("/index/info/{Project_id}")
async def info_project(request:Request,Project_id: str):
    #the request follow the app at startup and can store and gest all the data 
    
    project_model=await ProjectModel.create_instance(
        db_client=request.app.db_client)  # all the models now will treate with the client 
    
    # get the project or create a new one if it doesn't exist with same id
    project = await project_model.get_project_or_create_one(
        project_id = Project_id 
    )

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        parser_template=request.app.parser_template
    )

    collection_info = nlp_controller.get_vector_db_collection_info(
        project=project)
    
    print(collection_info)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "collection_info": collection_info,
            "message": ResponseEnumSignal.COLLECTION_INFO_RETRIEVED.value
        }
    )

@nlp_router.post ("/index/search/{Project_id}")
async def search_project(request:Request,Project_id: str , search_request: search_request):
    #the request follow the app at startup and can store and gest all the data 
    
    project_model=await ProjectModel.create_instance(
        db_client=request.app.db_client)  # all the models now will treate with the client

    # get the project or create a new one if it doesn't exist with same id
    project = await project_model.get_project_or_create_one(
        project_id = Project_id
    )

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        parser_template=request.app.parser_template
    )

    
    
    result = nlp_controller.search_vector_db_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit
    )
    if not result:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponseEnumSignal.VECTOR_DB_SEARCH_FAILED.value
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "search_results": [ res.dict() for res in result],
            "message": ResponseEnumSignal.VECTOR_DB_SEARCH_SUCCESS.value
        }
    )


@nlp_router.post ("/index/answer/{Project_id}") 
async def answer_rag(request:Request,Project_id: str , search_request: search_request):
    #the request follow the app at startup and can store and gest all the data 
    
    project_model=await ProjectModel.create_instance(
        db_client=request.app.db_client)  # all the models now will treate with the client

    # get the project or create a new one if it doesn't exist with same id
    project = await project_model.get_project_or_create_one(
        project_id = Project_id
    )

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        parser_template=request.app.parser_template
    )

    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit
    )

    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponseEnumSignal.RAG_ANSWER_FAILED.value
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history  # chat_history is already a list of dicts
        }
    )
