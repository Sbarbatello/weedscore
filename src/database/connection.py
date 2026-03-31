"""
Database connection handling for the Weedscore application.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from contextlib import contextmanager

def get_engine():
    """
    Creates and returns a SQLAlchemy engine configured from the NEON_URL
    environment variable.
    """
    load_dotenv()
    neon_url = os.getenv("NEON_URL")
    if not neon_url:
        raise ValueError("NEON_URL environment variable not set.")

    # Ensure sslmode is set for Neon
    if "?sslmode=require" not in neon_url:
        neon_url += "?sslmode=require"
        
    engine = create_engine(neon_url)
    return engine

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy session from the engine.
    """
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
