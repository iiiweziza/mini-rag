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
    project_model =await ProjectModel.create_instance(db_client=request.app.client_db)
    project = await project_model.get_project_or_create_one(
        project_id=Project_id
    )
    
    file_id = ProcessRequest.file_id
    chunk_size = ProcessRequest.chunk_size
    chunk_overlap = ProcessRequest.chunk_overlap
    do_reset = ProcessRequest.do_reset
    
    content = ProcessingController(project_id=Project_id).get_file_content(file_id=file_id)

    file_chunks = ProcessingController(project_id=Project_id).process_file_content(
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
            source_file=file_id  # Using file_id as the source file name
        )
        for i, chunk in enumerate(file_chunks)
    ]
    
    chunk_model =await ChunkModel.create_instance(db_client=request.app.client_db)

    if do_reset == 1 :
                # If do_reset is 1, delete all existing chunks for this project
                _= await chunk_model.delete_chunks_by_project_id(project_id=Project_id)
        
 
    # Insert the chunks into the database
    no_records_chunks = await chunk_model.insert_many_chunks(file_chunks_records)
    return JSONResponse(
        {
            "Result": ResponseEnumSignal.SUCCESS.value,
            "File ID": file_id,
            "Number of Chunks": no_records_chunks
        }
    )           
   