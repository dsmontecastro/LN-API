from flask import Blueprint, Response, abort, render_template, request
from jinja2 import TemplateNotFound
from json import dumps as to_json
from datetime import date
from typing import Any

from ._common import MODE, Encoder

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
                    to_json(results, cls = Encoder),
                    mimetype = 'application/json'
                )


            case MODE.SHOW:

                today = date.today()

                return render_template(
                    'blueprints/api.html',
                    entries = entries,
                    table = table_name,
                    today = today
                )


            case _:
                raise( TemplateNotFound(
                    name = 'Invalid URL',
                    message = 'Given MODE does not exist...'
                ))

    except KeyError: abort(500)
    except TemplateNotFound: abort(404)

# endregion --------------------------------------------------------------------------------------------------


# region : URL Parameter Handler -----------------------------------------------------------------------------

from ...common.isbn import to_isbn
from app.database.models.field import Fields, Opts

LIMIT = Opts.LIMIT.value
ORDER = Opts.ORDER.value
SORT_BY = Opts.SORT_BY.value

def get_params(table: str) -> dict[Any, Any]:

    params = {}

    params[LIMIT] = int(request.args.get(LIMIT) or '0')
    params[ORDER] = bool(request.args.get(ORDER)) or True
    params[SORT_BY] = request.args.get(SORT_BY) or Fields.DATE.value

    if table == 'All Tables': table = ''
    params[Fields.TABLE.value] = table

    for query in Fields.queries():

        field = query.name

        match(Fields[field.upper()]):

            case Fields.GENRES | Fields.CREDITS:

                value = request.args.getlist(field)

                if value:

                    if len(value) == 1:
                        if value[0]: value = value[0].split(',')
                        else: value = []

                    values = list(map(replace_underscore, value))
                    params[field] = values

            case Fields.ISBN:
                value = request.args.get(field)
                if value: params[field] = to_isbn(value)

            case _:
                value = request.args.get(field)
                if value: params[field] = value

    log.debug(f'Order: {params[ORDER]}')
    log.debug(f'Sort-By: {params[SORT_BY]}')
    return params


def replace_underscore(param: str):
    return param.replace('_', ' ')

# endregion --------------------------------------------------------------------------------------------------