from enum import Enum
from dateutil.parser import parse as dparse
from datetime import datetime, date as Date

from .table import Tables

class Opts(Enum):
    LIMIT = 'limit'
    ORDER = 'order'
    SORT_BY = 'sort_by'

class Fields(Enum):

    DATE = 'date'
    TABLE = 'table'
    TITLE = 'title'
    CREDITS = 'credits'
    GENRES = 'genres'
    FORMAT = 'format'
    PRICE = 'price'
    ISBN = 'isbn'

    @classmethod
    def queries(cls):
        return {
            cls.TITLE.value: '{string}',
            cls.DATE.value: '{YYYY-MM-DD}',
            cls.TITLE.value: '{string}',
            cls.CREDITS.value: '{string} (repeatable)',
            cls.GENRES.value: '{string} (repeatable)',
            cls.FORMAT.value: '{string}',
            cls.PRICE.value: '${X.X}',
            cls.ISBN.value: '{ISBN-Code}'
        }



class Media(object):

    def __init__(self, format: str, isbn: str, price: str):
        self.format = format.lower()
        self.isbn = isbn.lower()
        self.price = price

    def __str__(self):
        return f"""
            {self.format}
            ISBN: {self.isbn}
            PRICE: {self.price}
        """

    def json(self):
        return {
            'format': self.format,
            'price': self.price,
            'isbn': self.isbn
        }


class Entry(object):

    def __init__(self, table: Tables,
        url = '',
        date = '',
        title = '',
        cover = '',
        blurb = '',
        genres: list[str] = [],
        credits: list[str] = [],
        media: list[Media] = [],
    ):
        self.table: Tables = table

        # Raw Strings
        self.url: str = url
        self.title: str = title
        self.cover: str = cover
        self.blurb: str = blurb

        # List of Strings
        self.genres: list[str] = genres
        self.credits: list[str] = credits
        self.media: list[Media] = media
    
        # Requires processing
        self.date = dparse(date).date()


    def __str__(self):
        return f"""
            @{self.date.strftime('%m-%d-%y')}
            url = {self.url}
            title = {self.title}
            cover = {self.cover}
            blurb = {self.blurb}
            genres = {self.genres}
            credits = {self.credits}
            media = {self.media.__str__()}
        """

    def json(self):

        dict = self.__dict__
        dict['date'] = self.date.strftime('%Y-%m-%d')
        dict['media'] = [ m.json() for m in self.media ]
        dict['table'] = self.table.value.title

        return dict