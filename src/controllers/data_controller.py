from fastapi import UploadFile
from .base_controller import BaseController
from models.enums import ResponseEnumSignal
from .project_controller import ProjectController
import re
import os

class DataController(BaseController):
    '''here we will define the data controller 
    the data controller will take from super class BaseControllers''' 

    def __init__(self):
        super().__init__()  # Pass the settings to the BaseController constructor


    def validate_file(self, file:UploadFile):
        '''this function will validate the file type and size'''
        # here we want to check about type and size of the file and that is logic so we will build it in controller file 
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False , ResponseEnumSignal.TYPE_NOT_ALLOWED.value
        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False , ResponseEnumSignal.SIZE_LIMIT_EXCEEDED.value
        return True , ResponseEnumSignal.UPLOADED.value
    
    def generate_unique_file_name(self,org_file_name:str,uploading_id: str):

        random_string = self.generate_random_string()
        project_dir_path = ProjectController().get_project_dir(uploading_id=uploading_id)

        clean_file_name = self.get_clean_file_name(org_file_name)

        new_clean_file_path = os.path.join(project_dir_path,
                                           random_string + "_" + clean_file_name)
        
        while os.path.exists(new_clean_file_path):
            random_string = self.generate_random_string()
            new_clean_file_path = os.path.join(project_dir_path,
                                               random_string + "_" + clean_file_name)
            
        return new_clean_file_path   
                                         
    
    def get_clean_file_name(self, org_file_name: str):
        """Return a clean file name with only alphanumeric characters, underscores, and dots."""
   
        clean_file_name = org_file_name.strip().replace(" ", "_")
        clean_file_name = re.sub(r'[^\w.]', '', clean_file_name)
        return clean_file_name