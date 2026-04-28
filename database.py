from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────
# 🔌 DATABASE CONNECTION
# ─────────────────────────────────────────────

# This is the connection string to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine (connection to database)
engine = create_engine(DATABASE_URL)

# Create a session (like a conversation with database)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Get database session
    Opens a connection and closes it when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()