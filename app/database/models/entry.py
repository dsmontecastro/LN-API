from enum import Enum
from dateutil.parser import parse as dparse
from datetime import datetime, date as Date

from .media import Media
from .table import Tables
from .person import Person

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
            cls.DATE.value: '{YYYY-MM-DD} (equal/more than)',
            cls.TITLE.value: '{string}',
            cls.CREDITS.value: '{string} (repeatable)',
            cls.GENRES.value: '{string} (repeatable)',
            cls.FORMAT.value: '[audio/digital/physical]',
            cls.PRICE.value: '${X.X} (equal/less than)',
            cls.ISBN.value: '{ISBN-Code}'
        }


class Entry(object):

    def __init__(self, table: Tables,
        url = '',
        date = '',
        title = '',
        cover = '',
        blurb = '',
        genres: list[str] = [],
        media: list[Media] = [],
        credits: list[Person] = []
    ):
        self.table: Tables = table

        # Raw Strings
        self.url: str = url
        self.title: str = title
        self.cover: str = cover
        self.blurb: str = blurb

        # Lists
        self.genres: list[str] = genres
        self.media: list[Media] = media
        self.credits: list[Person] = credits
    
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

        dict['media'] = [ m.json() for m in self.media ]
        dict[Fields.DATE.value] = self.date.strftime('%Y-%m-%d')
        dict[Fields.TABLE.value] = self.table.value.title
        dict[Fields.CREDITS.value] = [ person.json() for person in self.credits ]

        return dict