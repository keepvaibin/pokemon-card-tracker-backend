# Task: Fix Backend Import Errors, Add Nested JSON API, and Push to GitHub

## Problem
The Flask backend fails to start due to:
```
ImportError: cannot import name 'Base' from 'app.db'
```
This happens because `Base` is not defined/exported in `app/db.py`.

Additionally:
- No nested JSON API endpoints exist yet.
- Git remote setup command was incorrect, so the repository isn’t linked to GitHub.

## Steps to Fix

### 1. Fix `Base` Import Error
Edit `app/db.py` to define and export the database connection, Base class, and session maker:

```python
# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pkmnadmin:A9d3F7vX2mQpN6rLbT5wZhC8KsGjYV4E@pokemon-tracker-db.postgres.database.azure.com:5432/card_db?sslmode=require"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### 2. Update `models.py` to use the new `Base`
Ensure:
```python
from .db import Base
```
is correct and all models inherit from `Base`.

### 3. Add Nested JSON API Endpoints
Example in `app/routes.py`:
```python
from flask import Blueprint, jsonify
from .db import SessionLocal
from .models import Card, Set

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/cards", methods=["GET"])
def get_cards():
    session = SessionLocal()
    cards = session.query(Card).all()
    data = []
    for card in cards:
        data.append({
            "id": card.id,
            "name": card.name,
            "set": {
                "id": card.set.id,
                "name": card.set.name
            }
        })
    session.close()
    return jsonify(data)
```

### 4. Git Remote Setup and Push
Run:
```bash
git remote add origin https://github.com/keepvaibin/pokemon-card-tracker-backend.git
git branch -M main
git push -u origin main
```

### 5. Test the Fix
```bash
source venv/bin/activate
python main.py
```
You should see the app start without import errors, and `/cards` should return nested JSON.
