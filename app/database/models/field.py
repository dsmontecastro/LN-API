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
        return {
            cls.TITLE.value:    Field('text', '{string}'),
            cls.CREDITS.value:  Field('text', '{string} (repeatable)', 'Separate items w/ commas (,)'),
            cls.GENRES.value:   Field('text', '{string} (repeatable)', 'Separate items w/ commas (,)'),
            cls.DATE.value:     Field('date', '{YYYY-MM-DD} (>=)'),
            cls.FORMAT.value:   Field('text', '[audio/digital/physical]', 'audio/digital/physical'),
            cls.PRICE.value:    Field('decimal', '${X.X} (<=)', '0.00'),
            cls.ISBN.value:     Field('text', '{ISBN-Code}', 'XXX-X-XXXXXX-XXX-X')
        }


class Field(object):

    def __init__(self, input: str, query: str, value: str = ''):
        self.input = input
        self.query = query
        self.value = value