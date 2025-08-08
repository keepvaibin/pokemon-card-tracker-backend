# app/db.py
from flask_sqlalchemy import SQLAlchemy

# This is our global db object that models will inherit from
db = SQLAlchemy()
