import pymongo as mongo

from models.entry import Entry


class DB():

    host = 'localhost'
    port = 27017

    db_name = ''
    table_name = 'entries'

    def __init__(self):
        self.client = mongo.MongoClient(self.host, self.port)
        self.database = self.client[self.db_name]
        self.table = self.database[self.table_name]

    def add_entry(self, entry: Entry):
        self.table.insert_one(entry.json())

    def add_entries(self, entries: list[Entry]):
        self.table.insert_many([ entry.json() for entry in entries ])

    def get_entry(self): print('WIP')