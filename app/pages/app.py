import os
from flask import Flask, request

from ..database import DB
db = DB()

def create_app(config = None):

    app = Flask(__name__, instance_relative_config = True)
    app.config.from_prefixed_env()

    # Extensions
    add_assets(app)
    add_blueprints(app)
    add_context(app)
    

    return app


# region : App Extensions ------------------------------------------------------------------------------------

def add_assets(app: Flask):

    from flask_assets import Environment, Bundle

    scss = Bundle(
        'scss/main.scss',
        depends = 'scss/*.scss',
        output  = 'css/styles.css',
        filters = ['libsass']
    )

    assets = Environment(app)
    assets.register('style', scss)
    scss.build()


def add_context(app: Flask):

    from database.models.table import Tables

    @app.context_processor
    def utility_processor():
    
        root = request.base_url
        routes = [ table for table in Tables ]
    
        return {
            'root': root,
            'routes': routes[1:],
        }

def add_blueprints(app: Flask):

    from .blueprints import index, tables

    app.register_blueprint(index.index)
    app.register_blueprint(tables.tables)


# endregion --------------------------------------------------------------------------------------------------