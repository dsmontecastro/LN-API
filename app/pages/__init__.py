from flask import Flask, request, render_template
from werkzeug.exceptions import HTTPException


def create_app(config = None):

    app = Flask(__name__, instance_relative_config = True)
    app.config.from_prefixed_env()
    load_singletons()

    # Extensions
    add_assets(app)
    add_blueprints(app)
    add_context(app)
    add_error_handling(app)

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


def add_error_handling(app: Flask):

    @app.errorhandler(Exception)
    def error(error: Exception):

        code: int = 500

        if isinstance(error, HTTPException):
            code = error.code or 500

        return render_template('home.html', code = code)


# endregion --------------------------------------------------------------------------------------------------