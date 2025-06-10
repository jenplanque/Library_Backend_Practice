from flask import Blueprint

books_bp = Blueprint("books_bp", __name__)

from . import routes  # Import routes to register them with the blueprint
