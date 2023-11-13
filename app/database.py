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

        self._client = mongo.MongoClient(host, port)
        self._database = self._client[self.db_name]
        self._table = self._database[self.table_name]

    def quit(self): self._client.close()

    def add_entry(self, entry: Entry):
        self._table.insert_one(entry.json())

    def add_entries(self, entries: list[Entry]):
        print(f'Adding entries... [{len(entries)}]')
    
        # self._table.insert_many([ entry.json() for entry in entries ])
    
        jsons = [ entry.json() for entry in entries ]
        self._table.insert_many(jsons)

    def get_entry(self): print('WIP')