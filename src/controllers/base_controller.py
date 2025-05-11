'''Here we will define the base controller.
The base controller will be used in all the controllers.'''

from helpers.config import get_settings, Settings

class BaseController:
    def __init__(self, settings: Settings):
        self.app_settings = settings  # This is the settings file that we will use in all the controllers