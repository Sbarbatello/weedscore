"""
Script to create the database tables in the Neon database.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database.models import Base
from database.connection import get_engine

def create_tables():
    """
    Initializes the database schema by creating all tables defined in models.py.
    """
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        print("Table created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
