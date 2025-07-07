"""Schemas for the data chunks in the database."""

from pydantic import BaseModel, Field , validator
from typing import Optional 
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")  # MongoDB's _id field
    project_id: str = Field(..., min_length=1)  # Foreign key to Project
    content: str = Field(..., min_length=1)  # The actual text content
    chunk_index: int = Field(..., ge=0)  # Index of this chunk in the document
    source_file: str = Field(..., min_length=1)  # Original file name
    chunks_file_asset_id: ObjectId  # the asset id of the file this chunk belongs to in assets database (collection)

    class Config:
        arbitrary_types_allowed = True  # Allow ObjectId type


    @classmethod #decorator to get the indexings of the model
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],
                "name": "project_id_chunk_index_1",
                "unique": False
            }
        ]