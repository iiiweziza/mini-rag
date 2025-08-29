'''Here we will define the base data model.
The base model will be used in all the data models.'''

from helpers.config import get_settings

class BaseDataModel:
    def __init__(self,db_client:object):
        self.db_client = db_client  # This is the database client that we will use in all the data models
        self.app_settings = get_settings()  # This is the settings file that we will use in all the data models
    
    