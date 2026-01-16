"""
WSGI configuration for PythonAnywhere deployment
This file is used by PythonAnywhere to run your Flask app
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/epic-free-games-notifier'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load environment variables from .env file
from dotenv import load_dotenv
dotenv_path = os.path.join(project_home, '.env')
load_dotenv(dotenv_path)

# Import your Flask app
from app import app as application
