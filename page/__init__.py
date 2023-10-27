import os
from flask import Flask, g, request


def create_app(config = None):

    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        # DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )


    if config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(config)


    # ensure the instance folder exists
    try: os.makedirs(app.instance_path)
    except OSError: pass

    # Extensions
    add_assets(app)
    add_blueprints(app)
    add_context(app)
    # add_database(app)
    

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


def add_blueprints(app: Flask):

    # from blueprints.index import index
    from .blueprints import index, tables

    app.register_blueprint(index.index)
    app.register_blueprint(tables.tables)


def add_context(app: Flask):

    @app.context_processor
    def utility_processor():
    
        root = request.base_url
        routes = list(app.url_map.iter_rules())
    
        return {
            'root': root,
            'routes': routes,
        }


# def add_database(app: Flask):


# endregion --------------------------------------------------------------------------------------------------