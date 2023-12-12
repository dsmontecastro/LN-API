from flask import Blueprint, Response, abort, render_template, request
from jinja2 import TemplateNotFound
from json import dumps as to_json
from typing import Any

from ._mode import MODE
from ..singletons import db
from ...common.logger import log
from ...database.models.table import Tables


# region : Blueprint -----------------------------------------------------------------------------------------

api = Blueprint('api', __name__, url_prefix = '/api/', template_folder = 'templates')

@api.route('/<string:mode>/<string:table_code>')
def page(mode: str, table_code: str):
    
    try: 

        table = Tables[table_code.upper()]
        table_name = table.value.title

        params = get_params(table_name)
        entries = db.query(params)


        match(MODE[mode.upper()]):

            case MODE.JSON:

                results = {
                    'count': len(entries),
                    'entries': entries
                }

                return Response(
                    to_json(results, default = str),
                    mimetype = 'application/json'
                )


            case MODE.SHOW:
                return render_template(
                    'blueprints/api.html',
                    table = table_name,
                    entries = entries
                )


            case _:
                raise( TemplateNotFound(
                    name = 'Invalid URL',
                    message = 'Given MODE does not exist...'
                ))

    except (KeyError, TemplateNotFound): abort(404)

# endregion --------------------------------------------------------------------------------------------------


# region : URL Parameter Handler -----------------------------------------------------------------------------

from app.database.models.field import Fields, Opts

LIMIT = Opts.LIMIT.value
ORDER = Opts.ORDER.value
SORT_BY = Opts.SORT_BY.value

def get_params(table: str) -> dict[Any, Any]:

    params = {}

    params[LIMIT] = int(request.args.get(LIMIT) or '0')
    params[ORDER] = bool(request.args.get(ORDER)) or True
    params[SORT_BY] = str(request.args.get(SORT_BY)) or Fields.DATE.value

    if table == 'All Tables': table = ''
    params[Fields.TABLE.value] = table

    for field in Fields.queries().keys():

        match(Fields[field.upper()]):

            case Fields.GENRES | Fields.CREDITS:

                value = request.args.getlist(field)

                if value:
                    values = map(replace_underscore, value)
                    params[field] = list(values)

            case _:
                value = request.args.get(field)
                if value: params[field] = value

    return params


def replace_underscore(param: str):
    return param.replace('_', ' ')

# endregion --------------------------------------------------------------------------------------------------