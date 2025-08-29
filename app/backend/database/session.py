from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://moderator:moderator@db:5432/moderator")
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

if USE_SQLITE:
    # For Hugging Face Spaces, use SQLite
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # For production with PostgreSQL
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
