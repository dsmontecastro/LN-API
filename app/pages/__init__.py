from flask import Flask, request

def create_app(config = None):

    app = Flask(__name__, instance_relative_config = True)
    app.config.from_prefixed_env()
    load_singletons()

    # Extensions
    add_assets(app)
    add_blueprints(app)
    add_context(app)

    return app


# region : App Extensions ------------------------------------------------------------------------------------


def load_singletons():
    from . import singletons


def add_assets(app: Flask):

    from flask_assets import Environment, Bundle

    scss = Bundle(
        'scss/body.scss',
        depends = 'scss/*.scss',
        output  = 'css/styles.css',
        filters = ['libsass']
    )

    assets = Environment(app)
    assets.register('style', scss)
    scss.build()


def add_blueprints(app: Flask):

    from .blueprints import index, api

    app.register_blueprint(index.index)
    app.register_blueprint(api.api)


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


def load_singletons():
    from . import singletons

# endregion --------------------------------------------------------------------------------------------------