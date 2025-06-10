# application/__init__.py
from flask import Flask
from .extensions import ma, limiter
from .models import db  # Import the SQLAlchemy instance from models

# from app.models import db
# from .blueprints.member import member_bp
# from app.blueprints.member import member_bp

from .blueprints.members import members_bp  # Import the members blueprint

# from .blueprints.books import books_bp  # Import the books blueprint
# from .blueprints.loans import loans_bp  # Import the loans blueprint


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    app.register_blueprint(members_bp, url_prefix="/members")
    # app.register_blueprint(books_bp, url_prefix="/books")
    # app.register_blueprint(loans_bp, url_prefix="/loans")

    return app
