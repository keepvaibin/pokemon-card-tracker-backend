from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://pkmnadmin:A9d3F7vX2mQpN6rLbT5wZhC8KsGjYV4E@pokemon-tracker-db.postgres.database.azure.com:5432/card_db?sslmode=require"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
