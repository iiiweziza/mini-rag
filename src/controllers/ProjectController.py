from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os

class ProjectController(BaseController):
    
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        project_dir = os.path.join(
            self.files_dir,
            str(project_id)
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir

    async def get_project_or_create_one(self, project_model, project_id: str, user_id: int = None):
        project = await project_model.get_project_or_create_one(
            project_id=project_id,
            user_id=user_id
        )
        return project