"""
Project Configuration
Loads environment variables and stores project settings.
"""

import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Google Gemini API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Default Gemini Model
DEFAULT_MODEL = "gemini-2.5-flash"

# Application Name
APP_NAME = "Natural Language to SQL Agent"