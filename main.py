from scraper import Scraper
from database.db import DB

from models.table import Tables


class Program:

    def __init__(self, proxy = '', headless = True):
        self.scraper = Scraper(proxy, headless)
        self.db = DB()

    def run(self):
        print('Running program...')
        self.scraper.run()

    def quit(self):
        self.scraper.quit()
    
    def test(self, table: Tables):
        self.scraper.test(table)


if __name__ == '__main__':
    proxy = ''
    app = Program(proxy = proxy, headless = False)
    # app.test(Target.ALL)
    app.test(Tables.SEA)
    app.quit()