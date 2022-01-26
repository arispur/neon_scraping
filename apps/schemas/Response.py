from pydantic import BaseModel
from typing import List

class BaseResponse(BaseModel):
    status: int = 200
    message: str = None

class ScrapResponse(BaseResponse):
    url: str = None
    total: int = 0
    pages: int = 0
    data: List = []
    time_start: str = None
    time_end: str = None

class DetailScrapResponse(BaseResponse):
    status: int = 200
    message: str = None
    url: str = None

class ErrorResponse(BaseResponse):
    pass

class SuccesResponse(BaseResponse):
    data: List = []
    pass