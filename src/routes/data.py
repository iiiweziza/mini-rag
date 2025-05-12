from fastapi import FastAPI, APIRouter, Depends,UploadFile
from helpers.config import get_settings, Settings  # importing settings from helpers file
import os 
import aiofiles
from controllers import DataController, ProjectController
import logging

from models.enums import ResponseEnumSignal

logs = logging.getLogger('uvicorn.error')


data_router = APIRouter(  

    prefix='/api/v1/data',          # you should write the prefix before any call page "host name" to run
    tags = ['/api/v1/data']           # can put related things in tags 
)

@data_router.post("/Upload/{uploading_id}")
async def upload_data(file: UploadFile, uploading_id: str,
                      app_settings: Settings = Depends(get_settings)):
    data_controller = DataController()
    is_valid, result_signal =data_controller.validate_file(file=file)
    if not is_valid:
        return result_signal

    project_dir_path = ProjectController().get_project_dir(uploading_id=uploading_id)
    file_path , file_id = data_controller.generate_unique_file_path(org_file_name=file.filename,
                                                           uploading_id=uploading_id)
    # file_id = random_string + "_" + clean_file_name
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):
                await out_file.write(chunk)
    except Exception as e:      
        logs.error(f"Error saving file: {e}")
        return ResponseEnumSignal.FILE_NOT_SAVED.value

    return {
        "Result":  result_signal,
        "File ID" : file_id  # Only return after file is saved 
    }