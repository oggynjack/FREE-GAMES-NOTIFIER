# Epic Free Games Notifier

🎮 **Never miss a free game again!** Automated notification system for Epic Games Store free games with a beautiful web dashboard.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### 🔔 Smart Notifications
- **Automatic Email Notifications** - Get emails when new free games are available
- **Smart History Tracking** - Never get duplicate notifications
- **Force Notify Option** - Manually trigger notifications for current games
- **Customizable Schedule** - Choose when to check (hourly, daily, manual)

### 🎨 Beautiful Web Dashboard
- **Modern UI** - Neon gaming theme with glassmorphism and animations
- **Admin Panel** - Full control over all settings
- **User Dashboard** - Personal view for each subscriber
- **Games Timeline** - iPhone Photos-style gallery of free games
- **Real-time Console** - Watch the scraper work live

### 🔒 Secure & Private
- **Admin Authentication** - Protect settings with login
- **Email Masking** - Privacy for public views
- **Device Fingerprinting** - Track users without cookies
- **Session Management** - Secure admin sessions

### 💾 Flexible Storage
- **JSON Mode** - Simple file-based storage (default)
- **MongoDB Mode** - Scalable database storage
- **Hybrid Mode** - Use both for redundancy

### 🎯 Advanced Filtering
- **Price Threshold** - Set maximum acceptable price
- **Currency Support** - INR, USD, EUR, GBP
- **DLC Exclusion** - Filter out add-ons
- **Beta Exclusion** - Skip early access games

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- SMTP email account (Gmail, Hostinger, etc.)
- (Optional) MongoDB for database mode

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/epic-free-games-notifier.git
   cd epic-free-games-notifier
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Copy `.env.example` to `.env` and edit:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your settings:
   ```env
   # SMTP Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL=your-email@gmail.com
   PASSWORD=your-app-password
   FROM_EMAIL=your-email@gmail.com
   TO_EMAIL=recipient@gmail.com
   
   # Admin Credentials
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-password
   SECRET_KEY=your-random-secret-key
   
   # Database (optional)
   DB_MODE=json
   MONGODB_URL=mongodb://localhost:27017/epic_games
   
   # Scheduling
   CHECK_FREQUENCY=daily
   PREFERRED_TIME=09:00
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   
   Open your browser to: `http://localhost:5000`

## 📖 Usage

### For Users (Registration)

1. Visit `http://your-server:5000/`
2. Enter your email address
3. You'll receive notifications automatically!

### For Admins

1. Navigate to `http://your-server:5000/login`
2. Login with your admin credentials
3. Access full control panel at `/controls`

#### Admin Panel Features:

**Database Configuration**
- Choose storage mode (JSON/MongoDB/Hybrid)
- Configure MongoDB connection
- Toggle database on/off

**Notification Settings**
- Add/remove email recipients
- Set check frequency
- Configure preferred check time
- Enable/disable notifications

**Game Filtering**
- Set price threshold
- Choose currency
- Toggle free-only mode
- Exclude DLC and beta games

**System Controls**
- Run notifier manually
- Force send notifications
- Clear games history
- View games timeline

## 🎮 How It Works

1. **Scraping**: Fetches free games from Epic Games Store API
2. **Filtering**: Applies your preferences (price, DLC, beta)
3. **History Check**: Compares against notification history
4. **Email Sending**: Sends beautiful HTML emails with game details
5. **Tracking**: Saves games to history and database

## 📧 Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication
2. Generate App Password:
   - Google Account → Security → 2-Step Verification → App Passwords
3. Use the 16-character app password in `.env`

### Hostinger/Custom SMTP

```env
SMTP_SERVER=smtp.hostinger.com
SMTP_PORT=587
EMAIL=your@domain.com
PASSWORD=your-password
FROM_EMAIL=your@domain.com
```

**Custom Display Name**: The system automatically uses "Epic Free Games Notifier" as the sender name while keeping your email address.

## 🔧 Advanced Configuration

### Scheduling (PythonAnywhere or Linux)

**Daily at 9 AM:**
```bash
# In PythonAnywhere Tasks or crontab
0 9 * * * cd /home/username/epic-free-games-notifier && python check_free_games.py
```

**Every 6 Hours:**
```python
# In scheduled_task.py
from check_free_games import main
main()
```

### MongoDB Setup

1. **Install MongoDB**
   ```bash
   # Ubuntu/Debian
   sudo apt install mongodb
   
   # Or use MongoDB Atlas (cloud)
   ```

2. **Update .env**
   ```env
   DB_MODE=mongodb
   MONGODB_URL=mongodb://localhost:27017/epic_games
   ```

### Custom Filtering

Edit `settings.json` or use the web dashboard:
```json
{
  "price_threshold": 500,
  "currency": "INR",
  "only_free_games": true,
  "exclude_dlc": true,
  "exclude_beta": true,
  "check_frequency": "daily",
  "preferred_time": "09:00"
}
```

## 📁 Project Structure

```
epic-free-games-notifier/
├── app.py                      # Flask web application
├── check_free_games.py         # Core scraping logic
├── database.py                 # Database abstraction layer
├── scheduled_task.py           # Scheduled task runner
├── wsgi.py                     # WSGI entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── settings.json               # User settings
├── notification_history.json   # Notification tracking
├── games_history.json          # Found games database
├── user_emails.json            # User subscriptions
├── templates/                  # HTML templates
│   ├── index.html             # Admin panel
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── user_view.html         # User dashboard
│   └── games_timeline.html    # Games gallery
├── static/                     # CSS & JS
│   ├── style.css              # Neon gaming theme
│   └── script.js              # Frontend logic
└── .github/                    # GitHub Actions
    └── workflows/
        └── scrape.yml         # Automated scraping
```

## 🌐 Deployment

### PythonAnywhere (Free Hosting)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

**Quick Steps:**
1. Upload files to PythonAnywhere
2. Install dependencies in virtual environment
3. Configure web app to use `wsgi.py`
4. Set up daily task for `check_free_games.py`
5. Update `.env` with your settings

### Docker (Advanced)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

```bash
docker build -t epic-games-notifier .
docker run -p 5000:5000 --env-file .env epic-games-notifier
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## ⚠️ Disclaimer

This project is for educational purposes. Use responsibly and respect Epic Games Store's terms of service. This tool simply aggregates publicly available information.

## 🙏 Acknowledgments

- Epic Games Store API
- Flask framework
- Beautiful gaming community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/epic-free-games-notifier/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/epic-free-games-notifier/discussions)

---

**Made with ❤️ for gamers who love free games!**

🎮 Happy Gaming! 🎮
