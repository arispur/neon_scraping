from apps.models import Model
from . import db

class News(Model):
    __table__ = 'news'
    __primary_key__ = 'newsid'
    __timestamps__ = False
    __incrementing__ = False

    def insert_scraping_data(data=None):
        return db.table('news').insert(data)
