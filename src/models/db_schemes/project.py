'''Schema for all the projects in the database, so we named it project.py.'''

from pydantic import BaseModel, Field , validator
from typing import Optional 
from bson.objectid import ObjectId


class Project(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")  # MongoDB's _id field
    project_id: str = Field(...,min_length=1) # the uploading id in upload route 

    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        return value
        
    class Config:
        # To Skip unnecessary conversion of ObjectId to string
        arbitrary_types_allowed = True

    @classmethod #decorator to get the indexings of the model
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],
                "name": "project_id_index_1", 
                "unique": True
            }
        ]
