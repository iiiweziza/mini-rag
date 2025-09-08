"""
In this file, we define the ProjectController class, which handles the logic for creating and managing projects.
The class inherits from BaseController, which provides common functionality for all controllers.
We will use it to control the uploaded files.
"""

from fastapi import UploadFile
from .base_controller import BaseController
from models.enums import ResponseEnumSignal
import os 

class ProjectController(BaseController):
    '''here we will define the data controller 
    the data controller will take from super class BaseControllers''' 

    def __init__(self):
        super().__init__()  # Pass the settings to the BaseController constructor

        # Now I want to call the files+ project id dir and create it if not exist

    def get_project_dir(self, project_id: str):
        '''this function will return the path of the project directory'''
        project_dir = os.path.join(self.uploaded_files_dir, str(project_id))
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir