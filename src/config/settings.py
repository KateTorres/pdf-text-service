"""
settings.py
-------------
Loads environment variables from .env and defines global configuration values.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_JOHN")

# API usage settings
MAX_REQ_PER_MIN = int(os.getenv("MAX_REQ_PER_MIN", 3))
MAX_TOKENS_PER_DAY = int(os.getenv("MAX_TOKENS_PER_DAY", 200000))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

# File Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")

# Create output directory, if does not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)