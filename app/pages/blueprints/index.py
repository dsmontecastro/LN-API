from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

index = Blueprint('index', __name__, template_folder = 'templates')

@index.route('/')
@index.route('/home')
def _index():
    try: return render_template('home.html')
    except TemplateNotFound: abort(404)