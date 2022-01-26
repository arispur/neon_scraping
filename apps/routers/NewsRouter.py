import json
from fastapi import APIRouter, Body, Response
from apps.controllers.NewsController import ControllerNews as news

router = APIRouter()

@router.get("/scraping_bola_net")
async def get_list_news_bola_net(response: Response, url: str, limit_pages: int):
    result = news.list_url_news_bola_net(url, limit_pages)
    response.status_code = result.status
    return result

@router.get("/scraping_detail_bola_net")
async def get_detail_news_bola_net(response: Response, url: str):
    result = news.get_detail_news_bola_net(url)
    response.status_code = result.status
    return result

@router.get("")
async def index_news(response: Response):
    result = news.index_news()
    response.status_code = result.status
    return result

@router.get("/{id}")
async def show_news(response: Response, id: str):
    result = news.show_news(id)
    response.status_code = result.status
    return result

@router.get("/periode/{date_start}/{date_end}", description = "Date format: Y-M-D")
async def periode_news(response: Response, date_start: str, date_end: str):
    result = news.periode_news(date_start, date_end)
    response.status_code = result.status
    return result