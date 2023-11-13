from . import database, scraper

from models.table import Tables


class App:

    def __init__(self, proxy = '', headless = True):
        self._scraper = scraper.Scraper(proxy, headless)
        self._db = database.DB()
    
    def run(self, table: Tables = Tables.ALL):
        print('Running app...')
        print(f'Table: {table.value['title']}')

        entries = self._scraper.run(table)
        self._db.add_entries(entries)

    def quit(self):
        self._scraper.quit()
        self._db.quit()

    def test(self, tables: list[Tables]):
        for table in tables: self.run(table)