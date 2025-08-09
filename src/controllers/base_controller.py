'''Here we will define the base controller.
The base controller will be used in all the controllers.'''

from helpers.config import get_settings, Settings
import os 
import random 
import string 

class BaseController:
    def __init__(self,settings: Settings = get_settings()):
        self.app_settings = settings  # This is the settings file that we will use in all the controllers

        self.base_dir = os.path.dirname(os.path.dirname(__file__))  # This is the base directory of the project
        self.uploaded_files_dir = os.path.join(self.base_dir,
                                               "assets","uploaded_files")  # This is the directory where we will store the uploaded files

        self.database_dir = os.path.join(self.base_dir,
                                         "assets","database")


    def generate_random_string(self, length: int = 12) -> str:
        """Generate a random string of given length."""
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choices(letters_and_digits, k=length))
    
    def get_database_path(self,db_name: str) :
        
        database_path = os.path.join(self.database_dir, db_name)

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        return database_path
        
