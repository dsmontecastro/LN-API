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
            cls.CREDITS.value:  Field('text', '{string} (repeatable)'),
            cls.GENRES.value:   Field('text', '{string} (repeatable)'),
            cls.DATE.value:     Field('date', '{YYYY-MM-DD} (equal/more than)'),
            cls.FORMAT.value:   Field('text', '[audio/digital/physical]'),
            cls.PRICE.value:    Field('decimal', '${X.X} (equal/less than)'),
            cls.ISBN.value:     Field('text', '{ISBN-Code}')
        }


class Field(object):

    def __init__(self, input: str, query: str):
        self.input = input
        self.query = query