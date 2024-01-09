from enum import Enum

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
        return [
            Field(cls.TITLE.value,   'text',   '{string}'),
            Field(cls.CREDITS.value, 'text',   '{string} (repeatable)', ' Separate items w/ commas (,)'),
            Field(cls.GENRES.value,  'text',   '{string} (repeatable)', ' Separate items w/ commas (,)'),
            Field(cls.DATE.value,    'date',   '{YYYY-MM-DD} (>=)'),
            Field(cls.FORMAT.value,  'text',   '[audio/digital/physical]', 'audio/digital/physical'),
            Field(cls.PRICE.value,   'number', '${X.X} (<=)', '0.00'),
            Field(cls.ISBN.value,    'text',   '{ISBN-Code}', 'X' * 13)
        ]


class Field(object):

    def __init__(self, name: str, input: str, query: str, value: str = ''):
        self.name = name
        self.input = input
        self.query = query
        self.value = value