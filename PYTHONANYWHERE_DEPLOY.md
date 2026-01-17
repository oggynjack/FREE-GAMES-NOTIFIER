# PythonAnywhere Deployment Guide

This guide details how to deploy the Epic Free Games Notifier on PythonAnywhere.

## 1. Setup

1.  **Sign up** for a PythonAnywhere account (free tier works).
2.  **Open a detailed console** (Bash).

## 2. Code

Clone your repository:
```bash
git clone https://github.com/yourusername/epic-free-games-notifier.git
cd epic-free-games-notifier
```

## 3. Virtual Environment

Create and activate a virtual environment:
```bash
mkvirtualenv --python=/usr/bin/python3.10 epicgames-env
pip install -r requirements.txt
```

## 4. Web App Configuration

1.  Go to the **Web** tab.
2.  **Add a new web app**.
3.  Choose **Manual Configuration** (select Python 3.10).
4.  **Virtualenv**: Enter the path (e.g., `/home/username/.virtualenvs/epicgames-env`).
5.  **Source code**: Enter the path (e.g., `/home/username/epic-free-games-notifier`).

6.  **WSGI Configuration File**:
    Click the link to edit the WSGI file. Replace contents with:
    ```python
    import sys
    import os
    
    # Add project directory to sys.path
    project_home = '/home/yourusername/epic-free-games-notifier'
    if project_home not in sys.path:
        sys.path = [project_home] + sys.path
    
    # Load .env variables
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_home, '.env'))
    
    # Import Flask app
    from app import app as application
    ```

## 5. Environment Variables

Create a `.env` file in your project folder with your production settings:
```bash
nano .env
```
(Paste your SMTP credentials and Secret Key here)

## 6. Static Files

In the **Web** tab, configure "Static files":
*   **URL**: `/static/`
*   **Directory**: `/home/username/epic-free-games-notifier/static`

## 7. Scheduled Tasks (Notifications)

Go to the **Tasks** tab.
Add a daily task (e.g., at 09:00 UTC):
```bash
/home/username/.virtualenvs/epicgames-env/bin/python /home/username/epic-free-games-notifier/check_free_games.py
```

## 8. Updates

To update your app later:
1.  **Pull changes**: `git pull origin main`
2.  **Reload app**: Go to Web tab and click "Reload".
