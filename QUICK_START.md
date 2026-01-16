# 🚀 Quick Start Guide for PythonAnywhere

## 5-Minute Setup

### 1️⃣ Upload Files
- Go to **Files** tab → Create folder `epic-free-games-notifier`
- Upload all project files to this folder

### 2️⃣ Create `.env` File
Create `/home/YOUR_USERNAME/epic-free-games-notifier/.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL=your_email@gmail.com
PASSWORD=your_app_password
TO_EMAIL=recipient@email.com
FROM_EMAIL=your_email@gmail.com
```

### 3️⃣ Install Dependencies
Open **Bash console**:
```bash
cd ~/epic-free-games-notifier
pip3 install --user -r requirements.txt
```

### 4️⃣ Edit Config Files
Replace `YOUR_USERNAME` in:
- `wsgi.py` (line 10)
- `scheduled_task.py` (line 10)

### 5️⃣ Create Web App
**Web** tab → **Add new web app** → **Manual configuration** → **Python 3.10**

Set WSGI file content (click to edit):
```python
import sys
import os

project_home = '/home/YOUR_USERNAME/epic-free-games-notifier'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

from app import app as application
```

Click **Reload** ✅

### 6️⃣ Set Up Daily Task
**Tasks** tab → Add:
```bash
python3 /home/YOUR_USERNAME/epic-free-games-notifier/scheduled_task.py
```
Time: `09:00` → **Create**

---

## ✅ Done!

Access your app: `YOUR_USERNAME.pythonanywhere.com`

Need help? See `DEPLOYMENT_GUIDE.md`
