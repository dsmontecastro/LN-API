from flask import Blueprint, Response, render_template, abort
from jinja2 import TemplateNotFound
from json import dumps as to_json

from ._common import MODE, Encoder

from ..singletons import db
from ...common.logger import log


# region : Blueprint -----------------------------------------------------------------------------------------

entry = Blueprint('entry', __name__, url_prefix = '/entry/', template_folder = 'templates')

@entry.route('/<string:mode>/<string:id>')
def page(mode: str, id: str):
    
    try:

        entry = db.get_entry(id)

        if not entry: raise TypeError


        match(MODE[mode.upper()]):

            case MODE.JSON:
                return Response(
                    to_json(entry, cls = Encoder),
                    mimetype = 'application/json'
                )

            case MODE.SHOW:
                return render_template(
                    'blueprints/entry.html',
                    entry = entry
                )

            case _:
                raise( TemplateNotFound(
                    name = 'Invalid URL',
                    message = 'Given MODE does not exist...'
                ))

    except TypeError: abort(500)
    except TemplateNotFound: abort(404)

# endregion --------------------------------------------------------------------------------------------------