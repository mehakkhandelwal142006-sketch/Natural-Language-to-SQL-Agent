"""
===========================================================
Database Operations
Supports Default DB & User Uploaded Files (CSV, Excel, SQLite)
===========================================================
"""

import os
import re
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

def get_connection(db_path=None):
    """
    Returns a database connection based on selected DB_TYPE or custom SQLite db_path.
    """
    target_db = db_path if db_path else SQLITE_DATABASE

    if DB_TYPE.lower() == "sqlite":
        db_dir = os.path.dirname(target_db)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        return sqlite3.connect(target_db)

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

def get_database_schema(db_path=None):
    """
    Reads all tables and columns from the database.
    Gemini uses this schema to generate SQL.
    """
    conn = get_connection(db_path=db_path)
    schema = ""

    try:
        if DB_TYPE.lower() == "sqlite":
            cursor = conn.cursor()
            tables = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            ).fetchall()

            for table in tables:
                table_name = table[0]
                schema += f"\nTable: {table_name}\n"

                columns = cursor.execute(
                    f"PRAGMA table_info('{table_name}');"
                ).fetchall()

                for column in columns:
                    schema += f"- {column[1]} ({column[2]})\n"

        else:
            tables = pd.read_sql("SHOW TABLES", conn)
            table_column = tables.columns[0]

            for table_name in tables[table_column]:
                schema += f"\nTable: {table_name}\n"
                columns = pd.read_sql(f"DESCRIBE `{table_name}`", conn)

                for _, row in columns.iterrows():
                    schema += f"- {row['Field']} ({row['Type']})\n"

    finally:
        conn.close()

    return schema


# ===========================================================
# Execute SQL Query
# ===========================================================

def execute_query(sql, db_path=None):
    """
    Executes SQL and returns a DataFrame.
    """
    conn = get_connection(db_path=db_path)

    try:
        df = pd.read_sql_query(sql, conn)
        return df

    finally:
        conn.close()

# ===========================================================
# Clean Table Name
# ===========================================================

def clean_table_name(filename):
    """
    Converts filename into a valid SQL table name.
    Example:
    My Sales Data.csv -> my_sales_data
    """

    name = os.path.splitext(filename)[0]
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip("_").lower()

    return name if name else "uploaded_table"


def load_custom_file_to_sqlite(uploaded_file, target_db="data/uploaded.db"):
    """
    Reads CSV, Excel, or SQLite files uploaded by the user
    and loads them into target_db.
    """

    # Create data folder if it doesn't exist
    db_dir = os.path.dirname(target_db)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    file_name = uploaded_file.name
    ext = os.path.splitext(file_name)[1].lower()

    # Remove previous uploaded database
    if os.path.isfile(target_db):
        os.remove(target_db)

    # ==========================================================
    # SQLite Database Upload
    # ==========================================================
    if ext in [".db", ".sqlite", ".sqlite3"]:

        with open(target_db, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return f"Successfully loaded SQLite database: {file_name}"

    # ==========================================================
    # CSV Upload
    # ==========================================================
    elif ext == ".csv":

        uploaded_file.seek(0)

        df = pd.read_csv(uploaded_file)
        print("CSV Loaded Successfully")
        print(df.head())
        print(df.shape)

        table_name = clean_table_name(file_name)

        conn = sqlite3.connect(target_db)

        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )
        cursor = conn.cursor()

        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()

print("Tables in uploaded.db:", tables)

        conn.close()

        return (
            f"Successfully created table "
            f"'{table_name}' ({len(df)} rows) "
            f"from {file_name}"
        )

    # ==========================================================
    # Excel Upload
    # ==========================================================
    elif ext in [".xlsx", ".xls"]:

        uploaded_file.seek(0)

        excel_file = pd.ExcelFile(uploaded_file)

        conn = sqlite3.connect(target_db)

        created_tables = []

        for sheet_name in excel_file.sheet_names:

            df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name
            )

            table_name = clean_table_name(
                f"{file_name}_{sheet_name}"
            )

            df.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False
            )

            created_tables.append(table_name)

        conn.close()

        return (
            f"Successfully created tables: "
            f"{', '.join(created_tables)} "
            f"from {file_name}"
        )

    # ==========================================================
    # Unsupported File
    # ==========================================================
    else:
        raise ValueError(
            "Unsupported file format. Please upload a CSV, Excel, or SQLite file."
        )

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

def get_tables(db_path=None):
    """
    Returns all table names from the selected database.
    """

    conn = get_connection(db_path=db_path)

    try:
        cursor = conn.cursor()

        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchall()

        return [table[0] for table in tables]

    finally:
        conn.close()

def preview_table(table_name, db_path=None, limit=100):
    """
    Returns first few rows from the selected table.
    """

    conn = get_connection(db_path=db_path)

    try:
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return pd.read_sql_query(query, conn)

    finally:
        conn.close()
    
def table_info(table_name, db_path=None):
    """
    Returns row count and column names.
    """

    conn = get_connection(db_path=db_path)

    try:

        rows = pd.read_sql_query(
            f"SELECT COUNT(*) AS total FROM {table_name}",
            conn
        ).iloc[0]["total"]

        columns = pd.read_sql_query(
            f"PRAGMA table_info('{table_name}')",
            conn
        )["name"].tolist()

        return rows, columns

    finally:
        conn.close()
