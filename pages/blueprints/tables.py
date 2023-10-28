from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

from models.table import Tables


tables = Blueprint('table', __name__, url_prefix = '/table', template_folder = 'templates')

@tables.route('/<code>')
def table(code: str):

    table = Tables[code.upper()]
    name = table.name
    title = table.value

    print(name, title)

    try: return render_template('base.html')
    except TemplateNotFound: abort(404)