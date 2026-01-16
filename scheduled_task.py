#!/usr/bin/env python3
"""
Scheduled task script for PythonAnywhere
This runs daily to check for new free games and send notifications
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/epic-free-games-notifier'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load environment variables
from dotenv import load_dotenv
dotenv_path = os.path.join(project_home, '.env')
load_dotenv(dotenv_path)

# Import and run the main function
from check_free_games import main

if __name__ == "__main__":
    print("Starting scheduled free games check...")
    main()
    print("Scheduled task completed!")
