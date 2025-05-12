from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    """
    Request schema for processing data.
    to be used as input of processing route
    """
    file_id: str
    chunk_size: Optional[int] = 100
    chunk_overlap: Optional[int] = 20
    do_reset : Optional[int] = 0


