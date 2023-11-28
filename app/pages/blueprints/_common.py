from typing import Any
from flask import request

# from app.database.models.table import Table
from app.database.models.entry import Fields
from ...common.logger import log


LIMIT = 'limit'

def get_params(table: str) -> dict[Any, Any]:

    params = {}

    params[LIMIT] = request.args.getlist(LIMIT) or 0
    params[Fields.TABLE.value] = table

    for field in Fields:

        match(field):

            case Fields.GENRES | Fields.CREDITS:

                param = field.value
                value = request.args.getlist(param)

                if value: params[param] = value


            case _:

                param = field.value
                value = request.args.get(param)

                if value: params[param] = value

    log.debug('> Params:')
    log.debug(f'>> {params}')

    return params
