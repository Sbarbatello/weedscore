"""
A temporary script to test the database connection.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database.connection import get_engine

def test_connection():
    """
    Tries to connect to the database and prints a success message.
    """
    try:
        engine = get_engine()
        connection = engine.connect()
        print("Connection Successful!")
        connection.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
