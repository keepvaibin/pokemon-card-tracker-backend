# __init__.py
import os
from flask import Flask
from .db import db
from .routes import bp as routes_bp

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev")

    # Bind db to app
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(routes_bp)

    with app.app_context():
        db.create_all()  # optional for local dev

    return app
