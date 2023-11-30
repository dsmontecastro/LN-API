from app import App

from app.database.models.table import Tables


if __name__ == '__main__':
    app = App(proxy = '', headless = True)
    app.run(Tables.ALL, limit = 10)
    app.quit()