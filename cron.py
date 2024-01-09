from app import App

from app.database.models.table import Tables


LIMIT = 50

if __name__ == '__main__':
    updater = App(proxy = '', headless = True)
    updater.run(Tables.ALL, LIMIT)
    # updater.run(Tables.CIW, LIMIT)
    # updater.run(Tables.JNC, LIMIT)
    # updater.run(Tables.KOD, LIMIT)
    # updater.run(Tables.SEA, LIMIT)
    # updater.run(Tables.YEN, LIMIT)
    updater.quit()
