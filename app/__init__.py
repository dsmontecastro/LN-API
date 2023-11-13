from . import _db
from scraper import Scraper

from models.table import Tables


class App:

    def __init__(self, proxy = '', headless = True):
        self._scraper = Scraper(proxy, headless)
        self._db = _db.DB()
    
    def run(self, table: Tables = Tables.ALL):
        print('Running app...')
        print(f'Target: {table}')
        entries = self._scraper.run()
        self._db.add_entries(entries)

    def quit(self):
        self._scraper.quit()
        self._db.quit()

    def test(self, tables: list[Tables]):
        for table in tables: self.run(table)


if __name__ == '__main__':
    app = App(proxy = '', headless = True)

    tables = [ Tables.CIW, Tables.KOD ]
    app.test(tables)

    app.quit()