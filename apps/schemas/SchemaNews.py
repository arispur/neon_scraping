from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class News(BaseModel):
    newsid: str = None
    news_tittle: str = None
    news_time: datetime  = None
    news_author: str  = None
    news_img: str  = None
    news_content: str  = None

class CreateNews(News):
    pass

class IndexNews(BaseModel):
    newsid: str = None
    news_tittle: str = None
    news_time: datetime = None
    news_author: str = None
    news_img: str = None

class ResponseNews(BaseModel):
    news_list: List[IndexNews]

class ResponseDetailNews(BaseModel):
    news_list: List[News]