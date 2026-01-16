# 🔐 Authentication & Privacy System

## Overview
Your Epic Free Games Notifier now has a complete authentication and privacy system!

---

## 🎯 Features Implemented

### 1. **User Privacy System**
- ✅ Each user is tracked by **IP address + browser fingerprint** (SHA-256 hash)
- ✅ Users only see **their own email** (others are hidden)
- ✅ Public view shows emails as `***@domain.com`
- ✅ Each device/browser is treated as a unique user

### 2. **Admin Authentication**
- ✅ Secure admin login with username/password
- ✅ Session-based authentication
- ✅ Admin sees **all emails** and can manage everything
- ✅ Logout button only shows for admins

### 3. **User Flow**

**New User:**
1. Visits `http://127.0.0.1:5000`
2. Sees registration page
3. Enters email to subscribe
4. Email is tied to their device/IP

**Returning User:**
1. Visits `http://127.0.0.1:5000`
2. Automatically sees their dashboard
3. Can view only their own email
4. Can unsubscribe anytime

**Admin:**
1. Visits `http://127.0.0.1:5000/login`
2. Enters credentials
3. Sees full admin dashboard
4. Can manage all emails and settings

---

## 🔑 Default Admin Credentials

**Username:** `admin`
**Password:** `admin123`

⚠️ **IMPORTANT:** Change these immediately!

### How to Change:

1. **Open `.env` file**
2. **Add/Update these lines:**
   ```env
   ADMIN_USERNAME=your_username
   ADMIN_PASSWORD=your_secure_password
   SECRET_KEY=your_random_secret_key_here
   ```
3. **Restart the server**

---

## 📁 New Files Created

1. **`app.py`** - Updated with authentication & user tracking
2. **`templates/login.html`** - Admin login page
3. **`templates/register.html`** - New user registration
4. **`templates/user_view.html`** - Personal user dashboard
5. **`templates/public.html`** - Public view with masked emails
6. **`user_emails.json`** - Maps device fingerprints to emails (auto-created)

---

## 🌐 Routes

| Route | Access | Description |
|-------|--------|-------------|
| `/` | Public | Auto-routes based on user status |
| `/login` | Public | Admin login page |
| `/logout` | Admin | Logout and clear session |
| `/public` | Public | View with masked emails |
| `/api/register_email` | Public | Register new email |
| `/api/unregister_email` | User | Remove own email |
| `/api/settings` | Admin | Manage all settings |
| `/api/user_emails` | Admin | View all user mappings |
| `/api/stream_run` | Public | Run scraper (SSE) |

---

## 🔒 Security Features

### Email Privacy
- **Users see:** Only their own email
- **Public sees:** `***@gmail.com` format
- **Admin sees:** All emails in full

### Device Tracking
```python
# Creates unique fingerprint from:
IP Address + User-Agent → SHA-256 Hash
```

This means:
- ✅ Same device/browser = Same user
- ✅ Different browser = Different user
- ✅ Different IP = Different user
- ✅ No cookies needed!

### Session Security
- Flask session with secret key
- Admin status stored in session
- Auto-expires on browser close

---

## 📊 Data Files

### `settings.json`
```json
{
  "emails": ["all@emails.com", "list@here.com"],
  "price_threshold": 500,
  "currency": "INR"
}
```

### `user_emails.json` (NEW!)
```json
{
  "hash_abc123": "user1@email.com",
  "hash_def456": "user2@email.com"
}
```

---

## 🚀 Testing the System

### Test as New User:
1. Visit `http://127.0.0.1:5000`
2. Should see registration form
3. Enter email, click Register
4. Should see personal dashboard

### Test as Admin:
1. Visit `http://127.0.0.1:5000/login`
2. Login: `admin` / `admin123`
3. Should see full admin panel with all emails
4. Logout button visible in header

### Test Privacy:
1. Open in **Incognito/Private** window
2. Visit `http://127.0.0.1:5000/public`
3. Should see masked emails: `***@domain.com`

---

## 🛡️ Best Practices

### For Production:

1. **Change Admin Password**
   ```env
   ADMIN_PASSWORD=YourSecurePassword123!
   ```

2. **Use Strong Secret Key**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

3. **Enable HTTPS**
   - Use SSL certificate
   - Prevents session hijacking

4. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   ```

5. **Backup `user_emails.json`**
   - Contains user-email mappings
   - Loss = users can't access their subscriptions

---

## 🎨 UI Changes

- ✅ Logout button only shows for admins
- ✅ Clean registration page for new users
- ✅ Personal dashboard for subscribed users
- ✅ Public view anyone can access

---

## 📝 Admin Tasks

### View All Users:
```bash
GET /api/user_emails
(Admin only)
```

### Manage Settings:
```bash
POST /api/settings
{
  "emails": [...],
  "price_threshold": 500
}
```

---

## 🔧 Troubleshooting

**Q: Logout button shows without login**
A: Fixed! Now uses `{% if is_admin %}` check

**Q: Can't login as admin**
A: Check `.env` file for correct credentials

**Q: User can't see their email**
A: Clear browser cache, re-register

**Q: Lost admin password**
A: Edit `.env` file, restart server

---

## 🎉 Summary

Your notifier now has:
- ✅ Privacy-first architecture
- ✅ Device-based user tracking
- ✅ Admin authentication
- ✅ Email masking for privacy
- ✅ Multi-user support
- ✅ Secure session management

**Refresh `http://127.0.0.1:5000` to see it in action!**
