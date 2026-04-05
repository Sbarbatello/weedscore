"""
Database connection handling for the Weedscore application.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional
from contextlib import contextmanager

# Global engine singleton to prevent connection leaks
_ENGINE: Optional[Engine] = None

def get_engine() -> Engine:
    """
    Creates and returns a singleton SQLAlchemy engine.
    """
    global _ENGINE
    if _ENGINE is None:
        load_dotenv()
        neon_url = os.getenv("NEON_URL")
        if not neon_url:
            raise ValueError("NEON_URL environment variable not set.")

        # Ensure sslmode is set for Neon
        if "?sslmode=require" not in neon_url:
            neon_url += "?sslmode=require"
            
        _ENGINE = create_engine(
            neon_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    return _ENGINE

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy session from the singleton engine.
    """
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
