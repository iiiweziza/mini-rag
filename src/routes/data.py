from fastapi import FastAPI, APIRouter, Depends, UploadFile, Request, Form
from helpers.config import get_settings, Settings  # importing settings from helpers file
import os 
import aiofiles
from controllers import DataController, ProjectController, ProcessingController
import logging
from typing import Optional

from routes.schemes.data_schema import ProcessRequest, UploadRequest
from models.project_model import ProjectModel
from models.db_schemes import DataChunk, Asset
from models.chunk_model import ChunkModel
from models.assets_model import AssetModel
from models.enums import ResponseEnumSignal , AssetsEnumType
from fastapi.responses import JSONResponse

logs = logging.getLogger('uvicorn.error')


data_router = APIRouter(  

    prefix='/api/v1/data',          # you should write the prefix before any call page "host name" to run
    tags = ['/api/v1/data']           # can put related things in tags 
)

@data_router.post("/Upload/{Project_id}")
async def upload_data(
    request: Request,
    Project_id: str,
    file: Optional[UploadFile] = None,
    url: Optional[str] = Form(None),
    chunk_size: Optional[int] = Form(100),
    chunk_overlap: Optional[int] = Form(20),
    app_settings: Settings = Depends(get_settings)
):
    """
    Unified upload endpoint that handles both file uploads and URL processing.
    
    For file uploads: Send file via multipart/form-data
    For URL uploads: Send url, chunk_size, and chunk_overlap via form data
    """
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    
    # Get or create project
    project = await project_model.get_project_or_create_one(
        project_id=Project_id
    )
    
    data_controller = DataController()
    
    # Check if this is a URL upload or file upload
    if url and url.strip():
        # URL Upload
        return await data_controller.process_url_upload(
            request, Project_id, project, data_controller, 
            url.strip(), chunk_size, chunk_overlap
        )
    elif file:
        # File Upload
        return await data_controller.process_file_upload(
            request, Project_id, project, data_controller, 
            file, app_settings
        )
    else:
        # Neither file nor URL provided
        return JSONResponse(
            status_code=400,
            content={"error": "Either a file or URL must be provided"}
        )




#putting processig in the same data router 
@data_router.post("/process/{Project_id}")
async def process_endpoint(request: Request, Project_id: str,
                      ProcessRequest: ProcessRequest):
    # Create a project model instance using the database client
    project_model =await ProjectModel.create_instance(db_client=request.app.db_client)
    # Get the project by ID or create it if it doesn't exist
    project = await project_model.get_project_or_create_one(
        project_id=Project_id
    )
    
    # Extract parameters from the request
    file_id = ProcessRequest.file_id
    chunk_size = ProcessRequest.chunk_size
    chunk_overlap = ProcessRequest.chunk_overlap
    do_reset = ProcessRequest.do_reset
    
    print(f"Requested Project_id (from path): {Project_id}")
    print(f"ProcessRequest.file_id: {ProcessRequest.file_id}")
    
    # Create an asset model instance for asset operations
    asset_model = await AssetModel.create_instance(
             db_client=request.app.db_client
        )

    projects_files_ids = {}
    if ProcessRequest.file_id:
        try:
            print(f"Looking for file with ID: {ProcessRequest.file_id}")
            print(f"Project ID from URL: {Project_id}")
            
            # Use the MongoDB ID directly since that's what we returned during upload
            asset_record = await asset_model.get_asset_record(
                asset_project_id=str(project.project_id),  # Convert to string for the method
                asset_name=ProcessRequest.file_id
            )
            
            if asset_record is None:
                # Return error if the file_id does not exist
                return JSONResponse(
                    {
                        "Result": ResponseEnumSignal.FILE_ID_ERROR.value,
                        "File ID": ProcessRequest.file_id,
                        "Project ID": project.project_id
                    },
                    status_code=404
                )
                
            print(f"Found asset record: {asset_record}")
            # If file_id is provided, use it to get the specific file
            projects_files_ids = {
                asset_record.asset_id: asset_record.asset_name
            }
        except Exception as e:
            logs.error(f"Error fetching asset with ID {ProcessRequest.file_id}: {e}")
            return JSONResponse(
                {
                    "Result": ResponseEnumSignal.FILE_ID_ERROR.value,
                    "File ID": ProcessRequest.file_id,
                    "Error": "Invalid file ID format"
                },
                status_code=400
            )

    else:
        # If no file_id is provided, get all files of the specified type in the project
        assets_project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.project_id,  # Pass as integer directly
            asset_type=AssetsEnumType.ASSETS_FILE.value
        )
        # Build a dictionary of all asset ids and names for the project
        projects_files_ids = {record.asset_id : record.asset_name
                              for record in assets_project_files
                              }
        print(f"Found asset file ids: {projects_files_ids}")

    # If no files are found, return a 404 error
    if len(projects_files_ids) == 0:
        return JSONResponse(
            {
                "Result": ResponseEnumSignal.NO_FILES_FOUND.value,
                "Project ID": Project_id
            },
            status_code=404
        )

    # Process each file in the project
    process_controller = ProcessingController(project_id=Project_id)

    no_records_chunks = 0
    no_files = 0

    # Initialize chunk model
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if do_reset == 1 :
                    # If do_reset is 1, delete all existing chunks for this project
        # Convert Project_id to integer for the database query
        try:
            project_id_int = int(Project_id)
            _ = await chunk_model.delete_chunks_by_project_id(project_id=project_id_int)
        except ValueError:
            # If conversion fails, log the error but continue processing
            logs.error(f"Invalid project ID format: {Project_id}")

    # Process files in reverse order (newest first)
    for chunks_file_asset_id, file_id in reversed(list(projects_files_ids.items())):
        # Get the file content using the file_id
        content = process_controller.get_input_content(file_id=file_id)

        if content is None or len(content) == 0:
            logs.error(f"File {file_id} is empty or not found.")
            continue  # Skip to the next file if content is empty or not found

        file_chunks = process_controller.process_input_content(
            file_content=content,
            file_id=file_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        print(f"Processed {len(file_chunks)} chunks for file {file_id}")
        
        # Store chunks in database
        chunk_objects = []
        for i, chunk in enumerate(file_chunks):
            chunk_object = DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i,
                chunk_project_id=project.project_id,
                chunk_asset_id=chunks_file_asset_id
            )
            chunk_objects.append(chunk_object)
            
        # Insert all chunks at once
        inserted_count = await chunk_model.insert_many_chunks(chunks=chunk_objects)
        print(f"Inserted {inserted_count} chunks into database for file {file_id}")
        
        no_records_chunks += inserted_count
        no_files += 1

    # Return success response
    return JSONResponse(
        status_code=200,
        content={
            "Result": ResponseEnumSignal.SUCCESS.value,
            "Processed Files": no_files,
            "Processed Chunks": no_records_chunks
        }
    )
