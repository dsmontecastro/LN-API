import mongoengine as me
from models.table import Tables


class Format(me.Document):
    format = me.StringField(unique = True, required = True)
    isbn = me.StringField(unique = True, default = '')
    price = me.StringField(default = '')


class Book(me.Document):

    # Non-String(s)
    url = me.URLField(unique = True, primary_key = True, required = True)
    table = me.EnumField(Tables, required = True)
    date = me.DateField()

    # String(s)
    title = me.StringField(default = '')
    cover = me.StringField(default = '')
    blurb = me.StringField(default = '')

    # String-List(s)
    genres = me.ListField(me.StringField(), default = [])
    credits = me.ListField(me.StringField(), default = [])

    # Embedded-Document List(s)
    media = me.EmbeddedDocumentListField(Format, default = [])