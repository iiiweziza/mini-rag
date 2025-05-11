from fastapi import UploadFile
from .base_controller import BaseController
from models.enums import ResponseEnumSignal

class DataController(BaseController):
    '''here we will define the data controller 
    the data controller will take from super class BaseControllers''' 

    def __init__(self, settings):
        super().__init__(settings)  # Pass the settings to the BaseController constructor


    def validate_file(self, file:UploadFile):
        '''this function will validate the file type and size'''
        # here we want to check about type and size of the file and that is logic so we will build it in controller file 
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False , ResponseEnumSignal.TYPE_NOT_ALLOWED.value
        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False , ResponseEnumSignal.SIZE_LIMIT_EXCEEDED.value
        return True , ResponseEnumSignal.UPLOADED.value