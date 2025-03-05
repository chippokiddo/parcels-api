import sqlite3
from config import DATABASE_PATH, logger

def get_db_connection():
    """Create a database connection with row factory."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def verify_db_connection():
    """Verify database connection is working."""
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database verification error: {str(e)}")
        return False