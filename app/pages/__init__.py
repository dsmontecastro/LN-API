from flask import Flask, render_template
from werkzeug.exceptions import HTTPException


def create_app():

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
        'scss/base.scss',
        depends = ['scss/*.scss', 'scss/**/*.scss'],
        output  = 'css/styles.css',
        filters = ['libsass']
    )

    assets = Environment(app)
    assets.register('style', scss)
    scss.build()


def add_blueprints(app: Flask):

    from .blueprints import api, entry, index

    app.register_blueprint(api.api)
    app.register_blueprint(entry.entry)
    app.register_blueprint(index.index)


def add_context(app: Flask):

    from ..database.models.table import ln_tables
    from ..database.models.entry import Fields

    @app.context_processor
    def utility_processor():
    
        return {
            'routes': ln_tables,
            'queries': Fields.queries()
        }


def add_error_handling(app: Flask):

    @app.errorhandler(Exception)
    def error(error: Exception):

        code: int = 500
        message: str = ''

        if isinstance(error, HTTPException):
            code = error.code or 500
            message = error.description or ''
        
        else: message = type(error).__name__

        return render_template('blueprints/index.html', code = code, message = message)


# endregion --------------------------------------------------------------------------------------------------