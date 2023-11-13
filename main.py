from app import App

from models.table import Tables


if __name__ == '__main__':
    app = App(proxy = '', headless = True)

    app.run(Tables.CIW)

    # tables = [ Tables.CIW, Tables.KOD ]
    # app.test(tables)

    app.quit()