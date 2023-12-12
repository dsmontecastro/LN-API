import os, datetime, pymongo as mongo
from bson.objectid import ObjectId
from bson import Decimal128

from typing import Any
from dotenv import load_dotenv
from re import compile, IGNORECASE

from ..common.logger import log
from .models.entry import Entry
from .models.field import Fields, Opts


MEDIA = 'media'
type Query = dict[str, Any]

class DB():

    db_name = 'ln-api'
    table_name = 'books'

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

        filter = { 'url': entry.url }
        update = entry.json()

        result = self.__table.replace_one(filter, update, upsert = True)

        return [result.modified_count, result.upserted_id]


    def get_entry(self, id: str):

        try:
            filter = { '_id': ObjectId(id) }
            result = self.__table.find_one(filter)
            return result

        except: return None


    def query(self, params: Query):

        limit: int = params.pop(Opts.LIMIT.value)
        sort_by: str = params.pop(Opts.SORT_BY.value)

        order: int = 1
        if not bool(params.pop(Opts.ORDER.value)): order = -1


        query: list[Query] = []
        query.append({ Fields.DATE.value: { '$gte': datetime.datetime.now().strftime('%Y-%m-%d') }})
        
        credits: list[Query] = []
        media: Query = {}
        cost: Query = {}


        for key in params.keys():

            value = params[key]
            field = Fields[key.upper()]

            match(field):

                case Fields.DATE:
                    query[0] = { key: { '$gte': value } }


                case Fields.GENRES:
                    values = map(self.__regex, value)
                    query.append({ key: { '$in': list(values) } })


                case Fields.CREDITS:
                    values = map(self.__regex, value)
                    for name in values:
                        credits.append({
                            key + '.name' : name
                        })


                case Fields.FORMAT | Fields.PRICE | Fields.ISBN:

                    finder: Query = {}

                    if field == Fields.PRICE:
                        try:
                            price = Decimal128(value)
                        except:
                            price = Decimal128('NaN')
                        finder = { '$lte': price }

                    else:
                        finder = {
                            '$regex': value,
                            '$options': 'i'
                        }

                    media[key] = finder


                case _:
                    value = str(value).replace('_', ' ')
                    query.append({ key: { '$regex': value,  '$options': 'i' } })



        if credits: query.append({ '$or': credits })
        if media: query.append({ 'media': { '$elemMatch': media } })
        if cost: query.append(cost)
        log.debug(f'Query: {query}')

        results = self.__table.find({ '$and': query })
        results.sort(sort_by, order).limit(limit)

        return list(results)


    def __regex(self, string: str):
        return compile(string, flags = IGNORECASE)