from apps.helper import Log
from apps.schemas import BaseResponse, ScrapResponse, DetailScrapResponse, ErrorResponse, SuccesResponse
from apps.schemas.SchemaNews import ResponseNews, CreateNews, ResponseDetailNews
from apps.helper.ConfigHelper import encoder_app
from main import PARAMS
from apps.models.NewsModel import News
from bs4 import BeautifulSoup
import requests
import pandas as pd
import codecs
import re
from apps.models import db
from datetime import datetime
import html5lib
from tqdm import tqdm
import hashlib

SALT = PARAMS.SALT.salt

class ControllerNews(object):
    @classmethod
    def list_url_news_bola_net(cls, url: str, limit_pages: int):
        time_start = cls.log_time()
        message_log = "Time start"
        Log.time(message_log)
        params = ''
        i = 0
        list_news = []

        if not (limit_pages < 21 and limit_pages > 0):
            e = "Out of limit pages"
            Log.error(e)
            result = ErrorResponse()
            result.status = 400
            result.message = str(e)
            message_log = "Time end"
            Log.time(message_log)
            return result

        while i < limit_pages:
            pages = f'{url}{params}'
            resp = requests.get(pages)
            if resp.status_code == 200:
                try:
                    soup = BeautifulSoup(resp.text, 'html5lib')
                    news = soup.select('div.item')

                    for j in range(len(news)):
                        list_news.append(
                            {
                                "url": news[j].select_one('a').attrs['href'],
                                "tittle": news[j].select_one('div.text a').text.strip()
                            }
                        )

                except:
                    e = "Error Soup"
                    Log.error(e)
                    result = ErrorResponse()
                    result.status = 404
                    result.message = str(e)
                    message_log = "Time end"
                    Log.time(message_log)
                    return result

            else:
                e = "Error Request"
                Log.error(e)
                result = ErrorResponse()
                result.status = resp.status_code
                result.message = str(e)
                message_log = "Time end"
                Log.time(message_log)
                return result

            i += 1
            params = f'index{i}.html'

        result = ScrapResponse()
        time_end = cls.log_time()
        result.time_start = time_start
        result.time_end = time_end
        result.url = url
        result.total = len(list_news)
        result.status = 200
        result.pages = limit_pages
        result.message = "Success scraping"
        result.data = list_news
        Log.info(result.message)
        message_log = "Time end"
        Log.time(message_log)
        return result

    @classmethod
    def get_detail_news_bola_net(cls, url: str):
        message_log = "Time start"
        Log.time(message_log)
        resp_detail = requests.get(url)
        newsid = hashlib.md5(url.encode())

        if News.where('newsid', '=', newsid.hexdigest()).get().serialize():
            result = DetailScrapResponse()
            result.status = 400
            result.url = url
            result.message = f"Data existing"
            Log.info(result.message)
            message_log = "Time end"
            Log.time(message_log)
            return result

        if resp_detail.status_code == 200:
            detail_news = BeautifulSoup(resp_detail.text, 'html5lib')

            try:
                news_tittle = detail_news.select_one('h1').text.strip()
            except:
                news_tittle = ''

            try:
                news_time = detail_news.select_one('div.newsdatetime').text.strip()
            except:
                news_time = ''

            try:
                news_author = detail_news.select_one('h2').text.strip()
                news_author = news_author.replace('|','')
            except:
                news_author = ''

            try:
                news_img = detail_news.select_one('div.news-headline-image.news img').attrs['data-src']
            except:
                news_img = ''

            try:
                news_content = [x.text for x in detail_news.select('div.ncont p')]
                news_content = ' '.join(news_content)
            except:
                news_content = ''

            news_tittle_clean = cls.cleanhtml(str(news_tittle))
            news_time_clean = cls.cleanhtml(str(news_time))
            news_time_clean = datetime.strptime(news_time_clean, '%d-%m-%Y %H:%M')
            news_author_clean = cls.cleanhtml(str(news_author))
            news_content_clean = cls.cleanhtml(str(news_content))

            news = {
                "newsid": newsid.hexdigest(),
                "news_tittle": news_tittle_clean,
                "news_time": news_time_clean,
                "news_author": news_author_clean,
                "news_img": news_img,
                "news_url": url,
                "news_content": news_content_clean
            }

            input_news = CreateNews(**news)

            try:
                with db.transaction():
                    if News.insert_scraping_data(input_news):
                        result = DetailScrapResponse()
                        result.status = 200
                        result.url = url
                        result.message = f"Success scraping - success save"
                        Log.info(result.message)
                        message_log = "Time end"
                        Log.time(message_log)
            except:
                result = DetailScrapResponse()
                result.status = 200
                result.url = url
                result.message = f"Success scraping - failed save"
                Log.info(result.message)
                message_log = "Time end"
                Log.time(message_log)

        else:
            e = "Error Request"
            Log.error(e)
            result = ErrorResponse()
            result.status = resp_detail.status_code
            result.message = str(e)
            message_log = "Time end"
            Log.time(message_log)
            return result

        return result

    @classmethod
    def savehtml(cls, name, value):
        file = open(name, 'w')
        file.write(value)
        file.close()

    @classmethod
    def cleanhtml(cls, raw_html):
        CLEANR = re.compile('<.*?>')
        cleantext = re.sub(CLEANR, '', raw_html)
        return cleantext

    @classmethod
    def index_news(cls):
        try:
            data = News.paginate(15, 2).serialize()
            result = SuccesResponse()
            result.status = 200
            result.message = "Success"
            result.data = ResponseNews(**{"news_list": data})
            Log.info(result.message)

        except Exception as e:
            result = ErrorResponse()
            Log.error(e)
            result.status = 400
            result.message = str(e)

        return result

    @classmethod
    def show_news(cls, id: str):
        try:
            data = News.where('newsid', '=', id).get().serialize()
            result = SuccesResponse()
            result.status = 200
            result.message = "Success"
            result.data = ResponseDetailNews(**{"news_list": data})
            Log.info(result.message)

        except Exception as e:
            result = ErrorResponse()
            Log.error(e)
            result.status = 400
            result.message = str(e)

        return result

    @classmethod
    def periode_news(cls, start: str, end: str):
        try:
            date_start = datetime.strptime(start, '%Y-%m-%d')
            date_end = datetime.strptime(end, '%Y-%m-%d')
        except:
            result = ErrorResponse()
            e = 'invalid date format'
            Log.error(e)
            result.status = 400
            result.message = str(e)

        try:
            data = db.table('news').where_between('news_time', [date_start, date_end]).get().serialize()
            result = SuccesResponse()
            result.status = 200
            result.message = "Success"
            result.data = ResponseNews(**{"news_list": data})
            Log.info(result.message)

        except Exception as e:
            result = ErrorResponse()
            Log.error(e)
            result.status = 400
            result.message = str(e)

        return result

    @classmethod
    def log_time(cls):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")