import os, pymongo as mongo
from dotenv import load_dotenv
from typing import Any

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

            log.debug(f'> Upserting: {entry.url}')

            id = self.add_entry(entry)

            log.debug(f'> Validation: {id}')


    def add_entry(self, entry: Entry):

        log.info(f'>> Upserted: {entry.title:.25s}')

        filter = {'_id': entry.url}
        update = entry.json()

        result = self.__table.replace_one(filter, update, upsert = True)

        return [result.modified_count, result.upserted_id]


    def query(self, params: dict[str, Any]):

        query: dict[str, Any] = {}

        limit = params.pop('limit')

        for key in params.keys():

            value = params[key]
            field = Fields[key.upper()]

            match(field):

                case Fields.DATE:
                    query[key] = { '$gte': value }

                case Fields.CREDITS | Fields.GENRES:
                    query[key] = { '$in': value }

                case Fields.FORMAT | Fields.PRICE | Fields.ISBN:
    
                    if not 'media' in query: query['media'] = []
    
                    query['media'].append({
                        'media': { '$elemMatch' : { key: value } }
                    })
    
                case _: query[key] = value

        results = self.__table.find(query).limit(limit)
        return list(results)