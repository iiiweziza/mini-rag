from fastapi import FastAPI, APIRouter, Depends,UploadFile
from helpers.config import get_settings, Settings  # importing settings from helpers file
import os 
from controllers import DataController


data_router = APIRouter(  

    prefix='/api/v1/data',          # you should write the prefix before any call page "host name" to run
    tags = ['/api/v1/data']           # can put related things in tags 
)

@data_router.post("/Upload/{uploading_id}")
async def upload_data(file:UploadFile,uploading_id:str,
    app_settings :Settings  = Depends(get_settings)):
    #here we want to check about type and size of the file and that is logic so we will build it in controller file 
    is_valid, result_signal = DataController(app_settings).validate_file(file=file)  # call the validate_file function from the controller file
    return result_signal    # return the result of the validation
