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
# Load Custom File (CSV, Excel, SQLite) into SQLite DB
# ===========================================================

def clean_table_name(filename):
    """
    Converts filename to a valid SQL table name.
    e.g., 'My Sales Data (2024).csv' -> 'my_sales_data_2024'
    """
    name = os.path.splitext(filename)[0]
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_').lower()
    return name or "uploaded_table"


def load_custom_file_to_sqlite(uploaded_file, target_db="data/uploaded.db"):
    """
    Reads CSV, Excel, or SQLite files uploaded by the user and loads them into target_db.
    Returns details about the created database/tables.
    """
    db_dir = os.path.dirname(target_db)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    file_name = uploaded_file.name
    ext = os.path.splitext(file_name)[1].lower()

    if ext in [".db", ".sqlite", ".sqlite3"]:
        # Save uploaded SQLite file directly
        with open(target_db, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return f"Successfully loaded SQLite database: {file_name}"

    elif ext == ".csv":
        df = pd.read_csv(uploaded_file)
        table_name = clean_table_name(file_name)

        conn = sqlite3.connect(target_db)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()

        return f"Successfully created table '{table_name}' ({len(df)} rows) from {file_name}"

    elif ext in [".xlsx", ".xls"]:
        excel_file = pd.ExcelFile(uploaded_file)
        conn = sqlite3.connect(target_db)
        created_tables = []

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            table_name = clean_table_name(f"{file_name}_{sheet_name}")
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            created_tables.append(table_name)

        conn.close()
        return f"Successfully created tables: {', '.join(created_tables)} from {file_name}"

    else:
        raise ValueError("Unsupported file format. Please upload a CSV, Excel, or SQLite file.")


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

