from scraper import Scraper
from database.db import DB

from models.table import Tables


class App:

    def __init__(self, proxy = '', headless = True):
        self.scraper = Scraper(proxy, headless)
        self.db = DB()

    def run(self):
        print('Running app...')
        self.scraper.run()

    def quit(self):
        self.scraper.quit()
    
    def test(self, table: Tables):
        self.scraper.test(table)


if __name__ == '__main__':
    proxy = ''
    app = App(proxy = proxy, headless = True)
    app.test(Tables.ALL)
    app.quit()