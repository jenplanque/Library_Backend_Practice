from app import create_app
from app.models import db

app = create_app("DevelopmentConfig")

with app.app_context():
    db.create_all()

    app.run()

# --- REMOVE ALL BELOW THIS LINE ---

# from flask import Flask, request, jsonify
# from typing import List
# from marshmallow import ValidationError
# from sqlalchemy import select
