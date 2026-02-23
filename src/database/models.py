"""
Data models for the Weedscore application.
"""

from sqlalchemy import create_engine, Column, Integer, DateTime, Boolean, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_solo = Column(Boolean, nullable=False)
    is_special_occasion = Column(Boolean, nullable=False)
    notes = Column(String)

    def __repr__(self):
        return f"<Session(id={self.id}, timestamp={self.timestamp})>"
