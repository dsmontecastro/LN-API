import os, pymongo as mongo
from dotenv import load_dotenv

from models.entry import Entry

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


    def add_entry(self, entry: Entry):
        self.__table.insert_one(entry.json())


    def add_entries(self, entries: list[Entry]):
        jsons = [ entry.json() for entry in entries ]
        self.__table.insert_many(jsons)


    def get_entry(self): print('WIP')