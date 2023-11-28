from flask import Blueprint, request, render_template, abort
from jinja2 import TemplateNotFound

# from ..app import db
from ._common import get_params
from ..singletons import db
from ...common.logger import log
from ...database.models.table import Tables
from ...database.models.entry import Fields


api = Blueprint('api', __name__, url_prefix = '/api', template_folder = 'templates')

@api.route('/<code>')
def table(code: str):

    table = Tables[code.upper()]
    table_name = table.value.title

    params = get_params(table_name)
    entries = db.query(params)
    
    try: return entries
    except TemplateNotFound: abort(404)