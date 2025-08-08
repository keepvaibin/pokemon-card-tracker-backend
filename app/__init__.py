# __init__.py
import os
from flask import Flask
from .db import db
from .routes import bp as routes_bp

from dotenv import load_dotenv
load_dotenv()

def create_app():
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fail fast so we never fall back to SQLite (ARRAY won’t compile there)
        raise RuntimeError("DATABASE_URL is required and must point to Postgres")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    # Only add the bind if TIMESCALE_URL is provided (avoid putting None in binds)
    timescale_url = os.getenv("TIMESCALE_URL")
    if timescale_url:
        app.config["SQLALCHEMY_BINDS"] = {"timescale": timescale_url}

    # Engine options must be a dict, never None
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})

    db.init_app(app)
    app.register_blueprint(routes_bp)

    # Avoid create_all() unless you truly need it and ONLY when pointing at Postgres.
    # Your schema already exists, so skip it.
    # with app.app_context():
    #     db.create_all()

    return app
