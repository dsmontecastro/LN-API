from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

# from ...models.table import Tables

tables = Blueprint('table', __name__, url_prefix = '/table', template_folder = 'templates')

@tables.route('/ciw')
def ciw():
    try: return render_template('base.html')
    except TemplateNotFound: abort(404)


@tables.route('/jnc')
def jnc():
    try: return render_template('base.html')
    except TemplateNotFound: abort(404)