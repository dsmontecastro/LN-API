from .scraper import Scraper
from .common.logger import log

from .database import DB
from .database.models.table import Tables


class App:

    MAX_LIMIT = 9999

    def __init__(self, proxy = '', headless = True):
    
        log.info('Creating app...')

        self.__scraper = Scraper(proxy, headless)
        self.__db = DB()

        log.info('Application Created!\n')


    def run(self, table: Tables = Tables.ALL, limit: int = MAX_LIMIT):

        if limit <= 0: limit = self.MAX_LIMIT

        log.info(f'Running app on [{table.value.title}]')

        entries = self.__scraper.run(table, limit)
        self.__db.add_entries(entries)
    
        log.info('Run finished.\n')


    def quit(self):

        log.info('Closing app...')

        self.__scraper.quit()
        self.__db.quit()

        log.info('Application closed.\n')