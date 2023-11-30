import os, pymongo as mongo
from dotenv import load_dotenv
from re import compile, IGNORECASE
from typing import Any

from ..common.logger import log
from .models.entry import Entry, Fields, Opts


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

            log.debug(f'> Upserting: { entry.url }')

            id = self.add_entry(entry)

            log.debug(f'> Validation: {id}')


    def add_entry(self, entry: Entry):

        log.info(f'>> Upserted: {entry.title:.25s}')

        filter = {'_id': entry.url}
        update = entry.json()

        result = self.__table.replace_one(filter, update, upsert = True)

        return [result.modified_count, result.upserted_id]


    def query(self, params: dict[str, Any]):

        limit: int = params.pop(Opts.LIMIT.value)
        sort_by: str = params.pop(Opts.SORT_BY.value)

        order: int = 1
        if not bool(params.pop(Opts.ORDER.value)): order = -1


        query: dict[str, Any] = {}

        for key in params.keys():

            value = params[key]
            field = Fields[key.upper()]

            match(field):

                case Fields.DATE:
                    query[key] = { '$gte': value }


                case Fields.CREDITS | Fields.GENRES:
                    values = map(self.__ignore_case, value)
                    query[key] = { '$in': list(values) }


                case Fields.FORMAT | Fields.PRICE | Fields.ISBN:
    
                    if not field.value in query:
                        query['media'] = { '$elemMatch': {} }

                    if field == Fields.PRICE:
                        query['media']['$elemMatch'][key] = {
                            '$lte': value
                        }

                    else:
                        query['media']['$elemMatch'][key] = {
                            '$regex': value,  '$options': 'i'
                        }


                case _:
                    value = str(value).replace('_', ' ')
                    query[key] = { '$regex': value,  '$options': 'i' }


        results = self.__table.find(query)
        results.sort(sort_by, order).limit(limit)

        return list(results)


    def __ignore_case(self, string: str):
        return compile(string, flags = IGNORECASE)