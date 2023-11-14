from models.table import Tables

from .logger import log
from .database import DB
from .scraper import Scraper


class App:

    def __init__(self, proxy = '', headless = True):
    
        log.info('Creating app...')

        self._scraper = Scraper(proxy, headless)
        self._db = DB()

        log.info('Application Created!\n')


    def run(self, table: Tables = Tables.ALL):

        log.info(f'Running app on [{table.value.title}]')

        entries = self._scraper.run(table)
        self._db.add_entries(entries)
    
        log.info('Run finished.\n')


    def quit(self):

        log.info('Closing app...')

        self._scraper.quit()
        self._db.quit()

        log.info('Application closed.\n')


    def test(self, tables: list[Tables]):
        for table in tables: self.run(table)