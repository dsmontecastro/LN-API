import os, pymongo as mongo
from dotenv import load_dotenv

from ..common.logger import log
from .models.entry import Entry, Fields


class DB():

    db_name = 'local_db'
    table_name = 'entries'

    def __init__(self):

        load_dotenv()
        host = os.environ.get('MONGO_HOST') or 'localhost'
        port = int(os.environ.get('MONGO_PORT') or '80')

        self.__client = mongo.MongoClient(host, port)
        self.__database = self.__client[self.db_name]
        self.__table = self.__database[self.table_name]


    def quit(self): self.__client.close()


    def add_entries(self, entries: list[Entry]):

        for entry in entries:

            log.info(f'> Upserting: {entry.url}')

            id = self.add_entry(entry)

            log.info(f'> Validation: {id}')


    def add_entry(self, entry: Entry):

        log.info(f'>> Upserted: {entry.title:.25s}')

        filter = {'_id': entry.url}
        update = entry.json()

        result = self.__table.replace_one(filter, update, upsert = True)

        return [result.modified_count, result.upserted_id]


    def get_entry(self, url):
        return self.__table.find_one({'_id': url})

    def get_entries(self, field: Fields, value: str):

        table = self.__table

        match(field):

            case Fields.DATE:
                return table.find({ field: { '$gte': value } })

            case Fields.CREDITS | Fields.GENRES:
                return table.find({ field: { '$in': value } })

            case Fields.FORMAT | Fields.ISBN:
                return table.find({ 'media': { field : value.lower() } })

            case Fields.PRICE:
                return table.find({ 'media': { field: { '$gte': value } } })

            case _:
                return table.find({ field: value})