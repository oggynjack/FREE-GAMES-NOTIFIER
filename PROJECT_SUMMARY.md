# Project Summary: Epic Free Games Notifier

## Project Overview
This project is an automated notification system that tracks free games on the Epic Games Store. It features a modern web dashboard for management and sends email alerts to subscribers. The system prevents duplicate notifications and allows for customized filtering.

## Current Status
- **Deployment**: Deployed on PythonAnywhere (Free Tier).
- **Environment**: Python 3.10 Virtual Environment.
- **Version Control**: Hosted on GitHub with auto-update capability.
- **State**: Fully functional and tested.

## Key Features

### Web Dashboard
- **Admin Panel**: Secure login for managing settings, database, and notifications.
- **User View**: Public-facing dashboard showing the latest free games and timeline.
- **Real-time Console**: View live logs of the scraping process.
- **Responsive Design**: Custom CSS with animations and mobile compatibility.

### Notification System
- **Email Alerts**: HTML-formatted emails with game details and images.
- **Smart Filtering**: Avoids duplicates and filters by price/type.
- **Scheduling**: Configurable check frequency (Hourly, Daily, Manual).

### Storage
- **Flexible Backend**: Supports JSON (default) or MongoDB storage.
- **History Tracking**: Maintains a record of all found games.

## Configuration

### Environment Variables (.env)
- **SMTP Settings**: Host, Port, Email, Password.
- **Admin Credentials**: Username, Password, Secret Key.
- **Database**: Mode (json/mongodb), Connection URL.
- **Schedule**: Frequency, Preferred Time.

### Settings (settings.json)
- Price threshold
- Currency
- Exclude DLC/Beta
- Email recipients list

## Deployment Guide

### PythonAnywhere Setup
1. Clone the repository to PythonAnywhere.
2. Create and activate a virtual environment.
3. Install dependencies from `requirements.txt`.
4. Configure the WSGI file to point to `app.py`.
5. Set up a scheduled task for `check_free_games.py` (e.g., daily at 09:00).

### Auto-Update Workflow
1. Push changes to GitHub.
2. Run the update script on PythonAnywhere (pulls latest code and reloads web app).
3. Verify changes on the live site.

## User Guide

### For Admins
- Login at `/login`.
- Use `/controls` to manage the system.
- "Run Notifier Now" triggers a manual check.
- "Force Send" bypasses history checks to test email delivery.

### For Users
- Visit the homepage to subscribe via email.
- View the "Timeline" to see past free games.

## Maintenance
- **Logs**: Check PythonAnywhere logs for errors.
- **Database**: `games_history.json` and `notification_history.json` store local data.
- **Updates**: Use Git to pull the latest version.

## Next Steps
- Implement advanced analytics.
- Add support for other game stores (Steam, GOG).
- Enhance mobile responsiveness.
