from pydantic import BaseModel
from typing import Optional

class push_reset(BaseModel):
    do_reset: Optional[int] = 0  # Flag to indicate if the index should be reset


class search_request(BaseModel):
    text: str  # The search query
    limit: Optional[int] = 5  # Number of results to return, default is 5
