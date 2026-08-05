import sqlite3
import pandas as pd

DATABASE_PATH = "data/company.db"


def get_connection():
    """
    Create a connection to the SQLite database.
    """
    return sqlite3.connect(DATABASE_PATH)


def execute_query(query):
    """
    Execute a SELECT query and return the result as a DataFrame.
    """
    conn = get_connection()

    try:
        result = pd.read_sql_query(query, conn)
        return result

    finally:
        conn.close()