from fastapi import FastAPI, APIRouter, Depends,UploadFile , Request
from helpers.config import get_settings, Settings  # importing settings from helpers file
import os 
import aiofiles
from controllers import DataController, ProjectController, ProcessingController
import logging

from routes.schemes.data_schema import ProcessRequest
from models.project_model import ProjectModel
from models.db_schemes.data_chunk import DataChunk
from models.db_schemes.assets_files import AssetsFiles
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
async def upload_data(request:Request,file: UploadFile, Project_id: str,
                      app_settings: Settings = Depends(get_settings)):
    #the request follow the app at startup and can store and gest all the data 

    project_model=await ProjectModel.create_instance(
        db_client=request.app.client_db)  # all the models now will treate with the client 
      
    # Add await here
    project = await project_model.get_project_or_create_one(
        project_id = Project_id 
    )

    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_file(file=file)
    if not is_valid:
        return result_signal

    # Change Project_id to uploading_id to match the parameter name
    project_dir_path = ProjectController().get_project_dir(project_id=Project_id)
    file_path, file_id = data_controller.generate_unique_file_path(org_file_name=file.filename,
                                                           project_id=Project_id)
    # file_id = random_string + "_" + clean_file_name
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):
                await out_file.write(chunk)
    except Exception as e:      
        logs.error(f"Error saving file: {e}")
        return ResponseEnumSignal.FILE_NOT_SAVED.value
    
    # Store file assets in the database
    asset_model = await AssetModel.create_instance(db_client=request.app.client_db) 

    asset_resource =  AssetsFiles(
         asset_project_id=project.id,  # Using the original project_id, not the MongoDB _id
         asset_type = AssetsEnumType.ASSETS_FILE.value,  # Using the enum value for asset type
         asset_name = file_id,
         asset_size = os.path.getsize(file_path),  # Get the file size
    )

    #Now we can insert the asset into the database by our new resource 
    asset_record = await asset_model.insert_asset(asset=asset_resource)

    return {
        "Result": result_signal,
        "File ID":str(asset_record.id),  # Using asset_name as the file ID
        #"Project_id": str(project._id)  # Return MongoDB's _id 
    }



#putting processig in the same data router 
@data_router.post("/process/{Project_id}")
async def process_endpoint(request: Request, Project_id: str,
                      ProcessRequest: ProcessRequest):
    # Create a project model instance using the database client
    project_model =await ProjectModel.create_instance(db_client=request.app.client_db)
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
    print(f"MongoDB Project _id (project.id): {project.id}")
    print(f"ProcessRequest.file_id: {ProcessRequest.file_id}")
    
    # Create an asset model instance for asset operations
    asset_model = await AssetModel.create_instance(
             db_client=request.app.client_db
        )

    projects_files_ids = {}
    if ProcessRequest.file_id:
        try:
            print(f"Looking for file with ID: {ProcessRequest.file_id}")
            print(f"Project ID from URL: {Project_id}")
            print(f"Project MongoDB ID: {project.id}")
            
            # Use the MongoDB ID directly since that's what we returned during upload
            asset_record = await asset_model.get_asset_by_mongodb_id(
                project_id=project.id,  # This is the MongoDB _id of the project
                mongodb_id=ProcessRequest.file_id
            )
            
            if asset_record is None:
                # Return error if the file_id does not exist
                return JSONResponse(
                    {
                        "Result": ResponseEnumSignal.FILE_ID_ERROR.value,
                        "File ID": ProcessRequest.file_id,
                        "Project ID": project.id
                    },
                    status_code=404
                )
                
            print(f"Found asset record: {asset_record}")
            # If file_id is provided, use it to get the specific file
            projects_files_ids = {
                asset_record.id: asset_record.asset_name
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
            project_id=project.id,  # Use the MongoDB ObjectId for asset_project_id
            asset_type=AssetsEnumType.ASSETS_FILE.value
        )
        # Build a dictionary of all asset ids and names for the project
        projects_files_ids = {record.id : record.asset_name
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
    chunk_model = await ChunkModel.create_instance(db_client=request.app.client_db)

    if do_reset == 1 :
                    # If do_reset is 1, delete all existing chunks for this project
        _= await chunk_model.delete_chunks_by_project_id(project_id=Project_id)


    # Process files in reverse order (newest first)
    for chunks_file_asset_id, file_id in reversed(list(projects_files_ids.items())):
        # Get the file content using the file_id
        content = process_controller.get_file_content(file_id=file_id)

        if content is None or len(content) == 0:
            logs.error(f"File {file_id} is empty or not found.")
            continue  # Skip to the next file if content is empty or not found

        file_chunks = process_controller.process_file_content(
            file_content=content,
            file_id=file_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        if file_chunks is None or len(file_chunks) == 0:
            return {
                "Result": ResponseEnumSignal.FAILED_PROCESS.value,
                "File ID": file_id
            }
        
        file_chunks_records = [
            DataChunk(
                content=chunk.page_content,
                project_id=Project_id,  # Using the original project_id, not the MongoDB _id
                chunk_index=i,
                source_file=file_id,  # Using file_id as the source file name
                chunks_file_asset_id=chunks_file_asset_id,  # Using the asset ID from the assets database,
                chunk_metadata={"text": chunk.page_content}  # Add metadata for each chunk
            )
            for i, chunk in enumerate(file_chunks)
        ]

        # Insert the chunks into the database
        no_records_chunks += await chunk_model.insert_many_chunks(file_chunks_records)
        no_files += 1
        
        if not do_reset:  # If not resetting, process only the latest file
            return JSONResponse(
                {
                    "Result": ResponseEnumSignal.SUCCESS.value,
                    "File ID": file_id,
                    "Number of Chunks": no_records_chunks,
                    "Processed Files": no_files,
                }
            )
    
    # Return final response after processing all files (for do_reset=True case)
    return JSONResponse(
        {
            "Result": ResponseEnumSignal.SUCCESS.value,
            "Number of Chunks": no_records_chunks,
            "Processed Files": no_files,
        }
    )
