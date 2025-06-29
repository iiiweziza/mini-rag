from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class AssetsFiles(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")  # MongoDB's _id field
    asset_project_id: str = Field(..., min_length=1)  # the uploading id in upload route
    asset_type: str = Field(..., min_length=1)  # type of the asset (e.g., image, video, document)
    asset_name: str = Field(..., min_length=1)  # name of the file
    asset_size: int = Field(gt=0, default=None)  # size of the file in bytes
    asset_config: dict = Field(default=None)  # configuration for the asset
    asset_published: datetime = Field(default=datetime.utcnow)  # date of publishing

    class Config:
        # To Skip unnecessary conversion of ObjectId to string
        arbitrary_types_allowed = True

    @validator("asset_project_id", pre=True, always=True)
    def validate_asset_project_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @classmethod #decorator to get the indexings of the model
    def get_indexes(cls):
        return [
            {
                "key": [("asset_project_id", 1)],
                "name": "asset_project_id_index_1", 
                "unique": False
            },{
                "key": [("asset_project_id", 1),
                        ("asset_name", 1)],
                "name": "asset_project_id_name_index_1",
                "unique": True
            }
        ]
