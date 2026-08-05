"""
===========================================================
Project Configuration
Natural Language to SQL Agent
===========================================================
"""

import os
from dotenv import load_dotenv

# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------

load_dotenv()

# ---------------------------------------------------------
# Application Settings
# ---------------------------------------------------------

APP_NAME = "🧠 SQL Chatbot"

APP_DESCRIPTION = (
    "Convert Natural Language into SQL Queries "
    "using Google's Gemini AI."
)

# ---------------------------------------------------------
# AI Model Configuration
# ---------------------------------------------------------

# Default model shown in the sidebar
DEFAULT_MODEL = "gemini-3.5-flash"

# Available Gemini Models
AVAILABLE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite"
]

# ---------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------

# Current supported database
DB_TYPE = "sqlite"

# SQLite Database Path
SQLITE_DATABASE = "data/company.db"

# ---------------------------------------------------------
# Future MySQL Support
# ---------------------------------------------------------

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")

# ---------------------------------------------------------
# Streamlit Settings
# ---------------------------------------------------------

PAGE_TITLE = "AI SQL Chatbot"

PAGE_ICON = "🧠"

LAYOUT = "wide"

# ---------------------------------------------------------
# Chat Settings
# ---------------------------------------------------------

CHAT_PLACEHOLDER = (
    "Ask something like: Show all employees working in the IT department"
)

# ---------------------------------------------------------
# Messages
# ---------------------------------------------------------

WELCOME_MESSAGE = """
👋 Welcome!

Ask any question in plain English.

Examples:

• Show all employees

• Show employees from HR

• Display employees earning more than 50000

• Count total employees

• Show average salary department wise
"""
