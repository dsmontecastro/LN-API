from enum import Enum
from dateutil.parser import parse as dparse
from datetime import datetime, date as Date

from .media import Media
from .field import Fields
from .table import Tables
from .person import Person


class Entry(object):

    def __init__(self, table: Tables,
        url: str = '',
        date: str = '',
        title: str = '',
        cover: str = '',
        blurb: str = '',
        genres: list[str] = [],
        media: list[Media] = [],
        credits: list[Person] = []
    ):
        self.table: Tables = table

        # Raw Strings
        self.url = url
        self.title = title
        self.cover = cover
        self.blurb = blurb

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