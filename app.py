from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import json
import os
import secrets
import hashlib
from datetime import datetime
from check_free_games import run_process as run_scraper, force_send_notifications, load_settings
from dotenv import load_dotenv
from database import init_database, get_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Admin credentials
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Initialize database
DB_MODE = os.getenv('DB_MODE', 'json')  # json, mongodb, hybrid
MONGODB_URL = os.getenv('MONGODB_URL', '')
init_database(mode=DB_MODE, mongodb_url=MONGODB_URL)

# Helper Functions
def get_user_fingerprint():
    """Create unique fingerprint from IP + User-Agent"""
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    fingerprint = hashlib.sha256(f"{ip}:{user_agent}".encode()).hexdigest()
    return fingerprint

def mask_email(email):
    """Mask email for privacy"""
    if '@' in email:
        local, domain = email.split('@', 1)
        return f"***@{domain}"
    return "***"

def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Main page - routes based on user status"""
    db = get_db()
    fingerprint = get_user_fingerprint()
    user_emails = db.read_user_emails()
    
    # Check if user has registered email
    user_email = user_emails.get(fingerprint)
    if user_email:
        settings = db.read_settings()
        user_settings = {
            'emails': [user_email],
            'price_threshold': settings.get('price_threshold', 500),
            'currency': settings.get('currency', 'INR')
        }
        return render_template('user_view.html', settings=user_settings, user_email=user_email)
    else:
        # New user - show registration
        return render_template('register.html')

@app.route('/controls')
def admin_panel():
    """Admin control panel - requires login"""
    print(f"[INFO] /controls accessed - session is_admin: {session.get('is_admin')}")
    if not session.get('is_admin'):
        print("[WARN] Not admin, redirecting to login")
        return redirect(url_for('login'))
    
    print("[SUCCESS] Admin verified, showing panel")
    db = get_db()
    settings = db.read_settings()
    return render_template('index.html', settings=settings, is_admin=True)

@app.route('/games')
def games_timeline():
    """Public games timeline"""
    db = get_db()
    history = db.read_games_history()
    return render_template('games_timeline.html', games=history)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.permanent = True
            session['is_admin'] = True
            session['username'] = username
            print(f"[SUCCESS] Login successful for {username}, session set: {session.get('is_admin')}")
            return jsonify({'success': True, 'redirect': '/controls'})
        print(f"[WARN] Login failed for {username}")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Already logged in?
    if session.get('is_admin'):
        return redirect(url_for('admin_panel'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/register_email', methods=['POST'])
def register_email():
    """Register user's email"""
    db = get_db()
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email required'}), 400
    
    fingerprint = get_user_fingerprint()
    
    user_emails = db.read_user_emails()
    user_emails[fingerprint] = email
    db.write_user_emails(user_emails)
    
    settings = db.read_settings()
    all_emails = settings.get('emails', [])
    if email not in all_emails:
        all_emails.append(email)
        settings['emails'] = all_emails
        db.write_settings(settings)
    
    return jsonify({'success': True, 'message': 'Email registered successfully'})

@app.route('/api/unregister_email', methods=['POST'])
def unregister_email():
    """Remove user's email"""
    db = get_db()
    fingerprint = get_user_fingerprint()
    user_emails = db.read_user_emails()
    
    if fingerprint in user_emails:
        email = user_emails[fingerprint]
        del user_emails[fingerprint]
        db.write_user_emails(user_emails)
        
        settings = db.read_settings()
        all_emails = settings.get('emails', [])
        if email in all_emails:
            all_emails.remove(email)
            settings['emails'] = all_emails
            db.write_settings(settings)
        
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    """Admin settings management"""
    db = get_db()
    
    if request.method == 'GET':
        settings = db.read_settings()
        # Add DB config
        settings['db_mode'] = db.mode
        settings['db_mongodb_url'] = MONGODB_URL if db.mode in ['mongodb', 'hybrid'] else ''
        return jsonify(settings)
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Handle DB mode change
        new_db_mode = data.get('db_mode')
        new_mongodb_url = data.get('db_mongodb_url')
        
        if new_db_mode and new_db_mode != db.mode:
            # Reinitialize database with new mode
            init_database(mode=new_db_mode, mongodb_url=new_mongodb_url)
            # Update .env file
            update_env_file('DB_MODE', new_db_mode)
            if new_mongodb_url:
                update_env_file('MONGODB_URL', new_mongodb_url)
        
        db = get_db()
        db.write_settings(data)
        load_settings()
        return jsonify({'message': 'Settings saved successfully'})

@app.route('/api/db_stats')
@login_required
def db_stats():
    """Get database statistics"""
    db = get_db()
    return jsonify(db.get_stats())

@app.route('/api/games_history')
def get_games_history():
    """Get games history"""
    db = get_db()
    history = db.read_games_history()
    return jsonify(history)

@app.route('/api/stream_run')
def stream_run():
    """Stream scraper results"""
    force = request.args.get('force', 'false').lower() == 'true'
    def generate():
        load_settings()
        db = get_db()
        
        import queue
        import threading
        q = queue.Queue()
        
        def callback(data):
            q.put(data)
            if data.get('type') == 'found':
                game = data.get('game')
                if game:
                    db.add_game_to_history(game)
        
        # Choose which function to run based on force parameter
        if force:
            target_func = force_send_notifications
        else:
            target_func = run_scraper
            
        t = threading.Thread(target=target_func, kwargs={'callback': callback})
        t.start()
        
        while t.is_alive() or not q.empty():
            try:
                data = q.get(timeout=0.1)
                yield f"data: {json.dumps(data)}\n\n"
            except queue.Empty:
                continue
        
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/public')
def public_view():
    """Public view with masked emails"""
    db = get_db()
    settings = db.read_settings()
    if 'emails' in settings:
        settings['emails'] = [mask_email(email) for email in settings['emails']]
    return render_template('public.html', settings=settings)

def update_env_file(key, value):
    """Update .env file"""
    env_path = '.env'
    lines = []
    found = False
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    with open(env_path, 'w') as f:
        for line in lines:
            if line.startswith(f'{key}='):
                f.write(f'{key}={value}\n')
                found = True
            else:
                f.write(line)
        
        if not found:
            f.write(f'{key}={value}\n')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
