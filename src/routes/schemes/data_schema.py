from pydantic import BaseModel, Field
from typing import Optional, Union

class ProcessRequest(BaseModel):
    """
    Request schema for processing data.
    to be used as input of processing route
    """
    file_id: str = None  # Optional file ID to process a specific file
    chunk_size: Optional[int] = 100
    chunk_overlap: Optional[int] = 20
    do_reset : Optional[int] = 0

class UploadRequest(BaseModel):
    """
    Unified request schema for uploading files or URLs.
    """
    url: Optional[str] = Field(None, description="URL to upload and process")
    chunk_size: Optional[int] = Field(100, description="Size of text chunks")
    chunk_overlap: Optional[int] = Field(20, description="Overlap between chunks")
    
    @property
    def is_url_upload(self) -> bool:
        """Check if this is a URL upload request"""
        return self.url is not None and self.url.strip() != ""
 

