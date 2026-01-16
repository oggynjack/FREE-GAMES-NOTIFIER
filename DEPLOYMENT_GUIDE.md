# PythonAnywhere Deployment Guide
## Deploy Epic Free Games Notifier to PythonAnywhere

---

## 📋 Prerequisites

- ✅ PythonAnywhere account (Free tier works!)
- ✅ Your project files ready
- ✅ SMTP email credentials (Gmail, Outlook, etc.)

---

## 🚀 Step-by-Step Deployment

### Step 1: Upload Files to PythonAnywhere

**Option A: Upload via Web Interface**

1. Go to **Files** tab in PythonAnywhere dashboard
2. Create a new directory: `epic-free-games-notifier`
3. Upload all these files:
   - `app.py`
   - `check_free_games.py`
   - `wsgi.py`
   - `scheduled_task.py`
   - `requirements.txt`
   - `.env` (create this file - see Step 2)
   - `settings.json`
   - `notification_history.json`
   - `templates/` folder (with `index.html`)
   - `static/` folder (with `style.css`, `script.js`)

**Option B: Upload via Git (Recommended)**

1. Open a **Bash console** in PythonAnywhere
2. Run these commands:
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/epic-free-games-notifier.git
cd epic-free-games-notifier
```

---

### Step 2: Create `.env` File

In PythonAnywhere **Files** tab or bash console:

1. Navigate to `/home/YOUR_USERNAME/epic-free-games-notifier/`
2. Create a new file named `.env`
3. Add your credentials:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL=your_email@gmail.com
PASSWORD=your_app_password
TO_EMAIL=recipient@email.com
FROM_EMAIL=your_email@gmail.com
```

**⚠️ For Gmail users:**
- Enable 2-Factor Authentication
- Generate an App Password: https://myaccount.google.com/apppasswords
- Use the App Password in the `.env` file (not your regular password)

---

### Step 3: Update Configuration Files

**Edit `wsgi.py`:**

Replace `YOUR_USERNAME` with your PythonAnywhere username:
```python
project_home = '/home/YOUR_PYTHONANYWHERE_USERNAME/epic-free-games-notifier'
```

**Edit `scheduled_task.py`:**

Same change - replace `YOUR_USERNAME`:
```python
project_home = '/home/YOUR_PYTHONANYWHERE_USERNAME/epic-free-games-notifier'
```

---

### Step 4: Install Dependencies

1. Open a **Bash console** in PythonAnywhere
2. Navigate to your project:
```bash
cd ~/epic-free-games-notifier
```

3. Install required packages:
```bash
pip3 install --user -r requirements.txt
```

---

### Step 5: Set Up Web App

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10** (or latest available)
5. Click **Next**

**Configure the web app:**

1. **Code section:**
   - **Source code:** `/home/YOUR_USERNAME/epic-free-games-notifier`
   - **Working directory:** `/home/YOUR_USERNAME/epic-free-games-notifier`

2. **WSGI configuration file:**
   - Click on the WSGI file link
   - **Delete all content** and replace with:
   
```python
import sys
import os

project_home = '/home/YOUR_USERNAME/epic-free-games-notifier'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from dotenv import load_dotenv
dotenv_path = os.path.join(project_home, '.env')
load_dotenv(dotenv_path)

from app import app as application
```

3. **Static files:**
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/epic-free-games-notifier/static`

4. Click **Reload** button at the top

---

### Step 6: Test Your Web App

1. Click on your web app URL (e.g., `YOUR_USERNAME.pythonanywhere.com`)
2. You should see your Epic Games Notifier interface!
3. Try clicking "Run Notifier Now" to test if it works

---

### Step 7: Set Up Daily Scheduled Task

1. Go to **Tasks** tab in PythonAnywhere dashboard
2. Scroll to **Scheduled tasks** section
3. Enter this command:
```bash
python3 /home/YOUR_USERNAME/epic-free-games-notifier/scheduled_task.py
```

4. Set the time (e.g., `09:00` for 9 AM daily)
5. Click **Create**

**⚠️ Free tier limitation:** Only 1 scheduled task per day

---

## 🎉 You're Done!

Your app is now live and will:
- ✅ Run automatically every day at your scheduled time
- ✅ Check for new free games
- ✅ Send email notifications
- ✅ Be accessible from anywhere via your PythonAnywhere URL

---

## 🔧 Troubleshooting

### Common Issues:

**1. "ImportError: No module named 'requests'"**
- Solution: Install dependencies in bash console:
```bash
pip3 install --user -r requirements.txt
```

**2. "500 Internal Server Error"**
- Check the **Error log** in the Web tab
- Make sure `.env` file exists with correct credentials
- Verify all file paths in `wsgi.py`

**3. "Email not sending"**
- Test your SMTP credentials
- For Gmail: Use App Password, not regular password
- Check `notification_history.json` - games might be already notified

**4. "Scheduled task not running"**
- Check **Tasks** tab for any error messages
- Make sure Python version matches (use `python3`)
- Verify file paths in `scheduled_task.py`

---

## 📝 Maintenance

### To Update Your Code:

**If using Git:**
```bash
cd ~/epic-free-games-notifier
git pull
```
Then click **Reload** in the Web tab

**If uploading manually:**
- Upload new files via Files tab
- Click **Reload** in the Web tab

### To View Logs:

- **Web app logs:** Web tab → Error log, Server log
- **Scheduled task logs:** Tasks tab → task history

---

## 📧 Support

If you encounter issues:
1. Check PythonAnywhere help pages: https://help.pythonanywhere.com/
2. Review error logs in Web and Tasks tabs
3. Verify all credentials in `.env` file

---

## 🎮 Enjoy Your Free Games!

Your notifier is now running 24/7 and will email you whenever new free games are available on Epic Games Store!
