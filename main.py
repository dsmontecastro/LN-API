from scraper import Scraper

from models.targets import Target


class Program:

    def __init__(self):
        self.scraper = Scraper()
        # self.db = DB()

    def run(self):
        print('Running program...')
        self.scraper.run()

    def quit(self):
        self.scraper.quit()
    
    def test(self, target: Target):
        self.scraper.test(target)


if __name__ == '__main__':
    app = Program()
    app.test(Target.JNC)