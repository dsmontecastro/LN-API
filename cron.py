from app import App

from app.database.models.table import Tables


LIMIT = 5

if __name__ == '__main__':
    updater = App(proxy = '', headless = True)
    updater.run(Tables.ALL, LIMIT)
    # update.run(Tables.CIW, LIMIT)
    # update.run(Tables.JNC, LIMIT)
    # update.run(Tables.KOD, LIMIT)
    # update.run(Tables.SEA, LIMIT)
    # update.run(Tables.YEN, LIMIT)
    updater.quit()
