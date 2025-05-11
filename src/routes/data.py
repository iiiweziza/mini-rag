from fastapi import FastAPI, APIRouter, Depends,UploadFile
from helpers.config import get_settings, Settings  # importing settings from helpers file
import os 
import aiofiles
from controllers import DataController, ProjectController


data_router = APIRouter(  

    prefix='/api/v1/data',          # you should write the prefix before any call page "host name" to run
    tags = ['/api/v1/data']           # can put related things in tags 
)

@data_router.post("/Upload/{uploading_id}")
async def upload_data(file: UploadFile, uploading_id: str,
                      app_settings: Settings = Depends(get_settings)):
    is_valid, result_signal = DataController(app_settings).validate_file(file=file)
    if not is_valid:
        return result_signal

    project_dir_path = ProjectController(app_settings ).get_project_dir(uploading_id=uploading_id)
    file_path = os.path.join(project_dir_path, file.filename)

    async with aiofiles.open(file_path, 'wb') as out_file:
        while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):
            await out_file.write(chunk)

    return result_signal  # Only return after file is saved