from flask import Blueprint, request, render_template, abort
from jinja2 import TemplateNotFound
from typing import Any
from enum import Enum

from ..singletons import db
from ...common.logger import log
from ...database.models.table import Tables


# region : Constants -----------------------------------------------------------------------------------------

class MODE(Enum):
    API = 'api'
    SHOW = 'show'

# endregion --------------------------------------------------------------------------------------------------


# region : Blueprint -----------------------------------------------------------------------------------------

api = Blueprint('api', __name__, template_folder = 'templates')

@api.route('/<string:mode>/<string:table_code>')
def page(mode: str, table_code: str):

    table = Tables[table_code.upper()]
    table_name = table.value.title

    params = get_params(table_name)
    entries = db.query(params)
    
    try: 

        match(MODE[mode.upper()]):

            case MODE.API:

                return {
                    'count': len(entries),
                    'entries': entries
                }


            case MODE.SHOW:
                return render_template(
                    'main.html',
                    table = table_name,
                    entries = entries
                )


            case _:
                raise( TemplateNotFound(
                    name = 'Invalid URL',
                    message = 'Given MODE does not exist...'
                ))

    except TemplateNotFound: abort(404)

# endregion --------------------------------------------------------------------------------------------------


# region : URL Parameter Handler -----------------------------------------------------------------------------

from app.database.models.entry import Fields, Opts

LIMIT = Opts.LIMIT.value
ORDER = Opts.ORDER.value
SORT_BY = Opts.SORT_BY.value

def get_params(table: str) -> dict[Any, Any]:

    params = {}

    params[LIMIT] = int(request.args.get(LIMIT) or '0')
    params[ORDER] = bool(request.args.get(ORDER)) or True
    params[SORT_BY] = str(request.args.get(SORT_BY)) or Fields.URL.value

    params[Fields.TABLE.value] = table

    for field in Fields:

        match(field):

            case Fields.GENRES | Fields.CREDITS:

                param = field.value
                value = request.args.getlist(param)

                if value:
                    values = map(replace_underscore, value)
                    params[param] = list(values)

            case _:

                param = field.value
                value = request.args.get(param)

                if value: params[param] = value

    return params


def replace_underscore(param: str):
    return param.replace('_', ' ')

# endregion --------------------------------------------------------------------------------------------------