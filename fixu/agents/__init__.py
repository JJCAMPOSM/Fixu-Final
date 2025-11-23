from flask import Blueprint

bp = Blueprint('agents', __name__, url_prefix='/agents')

from . import routes
