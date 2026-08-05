"""
===========================================================
Database Operations
===========================================================
"""

import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from config import (
    DB_TYPE,
    SQLITE_DATABASE,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
)


# ===========================================================
# Database Connection
# ===========================================================

def get_connection():
    """
    Returns a database connection based on the selected DB_TYPE.
    """

    if DB_TYPE.lower() == "sqlite":
        return sqlite3.connect(SQLITE_DATABASE)

    elif DB_TYPE.lower() == "mysql":
        engine = create_engine(
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        )
        return engine.connect()

    else:
        raise Exception("Unsupported Database Type")


# ===========================================================
# Get Database Schema
# ===========================================================

def get_database_schema():
    """
    Reads all tables and columns from the database.
    Gemini uses this schema to generate SQL.
    """

    conn = get_connection()

    schema = ""

    try:

        if DB_TYPE.lower() == "sqlite":

            cursor = conn.cursor()

            tables = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ).fetchall()

            for table in tables:

                table_name = table[0]

                schema += f"\nTable: {table_name}\n"

                columns = cursor.execute(
                    f"PRAGMA table_info({table_name});"
                ).fetchall()

                for column in columns:

                    schema += f"{column[1]} ({column[2]})\n"

        else:

            tables = pd.read_sql(
                "SHOW TABLES",
                conn
            )

            table_column = tables.columns[0]

            for table_name in tables[table_column]:

                schema += f"\nTable: {table_name}\n"

                columns = pd.read_sql(
                    f"DESCRIBE {table_name}",
                    conn
                )

                for _, row in columns.iterrows():

                    schema += f"{row['Field']} ({row['Type']})\n"

    finally:

        conn.close()

    return schema


# ===========================================================
# Execute SQL Query
# ===========================================================

def execute_query(sql):
    """
    Executes SQL and returns a DataFrame.
    """

    conn = get_connection()

    try:

        df = pd.read_sql_query(sql, conn)

        return df

    finally:

        conn.close()


# ===========================================================
# Validate SQL
# ===========================================================

def validate_sql(sql):
    """
    Basic SQL validation.
    """

    sql = sql.strip().lower()

    valid_keywords = [
        "select",
        "insert",
        "update",
        "delete",
        "create",
        "drop",
        "alter",
        "with"
    ]

    return any(sql.startswith(keyword) for keyword in valid_keywords)
