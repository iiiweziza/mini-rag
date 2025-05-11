'''Here we will define the base controller.
The base controller will be used in all the controllers.'''

from helpers.config import get_settings, Settings
import os 

class BaseController:
    def __init__(self, settings: Settings):
        self.app_settings = settings  # This is the settings file that we will use in all the controllers

        self.base_dir = os.path.dirname(os.path.dirname(__file__))  # This is the base directory of the project
        self.uploaded_files_dir = os.path.join(self.base_dir,"assets","uploaded_files")  # This is the directory where we will store the uploaded files