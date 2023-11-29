from flask import Blueprint, render_template
from werkzeug.exceptions import HTTPException

err = Blueprint('err', __name__, url_prefix = '/err', template_folder = 'templates')

@err.errorhandler(Exception)
def error(code: int):
    return render_template('err.html'), code