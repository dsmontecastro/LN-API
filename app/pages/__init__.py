# import os
from flask import Flask, request

from . import singletons   # initializes module as singleton
# db = DB()

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

    from ..database.models.table import ln_tables

    @app.context_processor
    def utility_processor():
    
        root = request.base_url
        routes = ln_tables
    
        return {
            'root': root,
            'routes': routes,
        }

def add_blueprints(app: Flask):

    from .blueprints import index, tables

    app.register_blueprint(index.index)
    app.register_blueprint(tables.tables)


# endregion --------------------------------------------------------------------------------------------------