import os
import sqlite3
import datetime
import random
import string
import csv
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_handler # Import our new module

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'), 
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))
app.secret_key = 'super_secret_security_key_demo_only'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

DATABASE = os.path.join(os.path.dirname(__file__), 'security_app.db')

# Try to init Firebase on startup
firebase_handler.init_firebase()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_path = app.config.get('DATABASE', DATABASE)
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # Users table
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            access_revoked BOOLEAN DEFAULT 0,
            is_isolated BOOLEAN DEFAULT 0
        )''')
        # Logs table
        db.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        # Devices table (MDM) - Enhanced for full controls
        db.execute('''CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            device_name TEXT,
            device_type TEXT,
            status TEXT,
            last_seen DATETIME,
            is_encrypted BOOLEAN DEFAULT 0,
            is_locked BOOLEAN DEFAULT 0,
            is_isolated BOOLEAN DEFAULT 0,
            risk_score INTEGER DEFAULT 0
        )''')
        
        # Seed default admin if not exists
        try:
            admin_check = db.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
            if not admin_check:
                hashed = generate_password_hash('admin123')
                db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', hashed, 'admin'))
            
            # Seed demo user
            user_check = db.execute("SELECT * FROM users WHERE username = 'demo'").fetchone()
            if not user_check:
                hashed = generate_password_hash('demo123')
                db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('demo', hashed, 'user'))
            
            # NO dummy devices seeded by default. Users must enroll via MDM.
            
            db.commit()
        except Exception as e:
            print(f"DB Init Error: {e}")

# Application Routes

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Security Anomaly Detection Helpers
def check_anomaly(user_id, user_name):
    alerts = []
    current_time = datetime.datetime.now()
    
    # 1. Check Office Hours (9 AM - 6 PM)
    if not (9 <= current_time.hour < 18):
        alerts.append("After-hours access detected")

    # 2. Check Session Duration
    if 'login_time' in session:
        try:
            login_time = datetime.datetime.fromisoformat(session['login_time'])
            if (current_time - login_time).total_seconds() > 28800: # 8 hours
                alerts.append("Abnormal session duration (>8h)")
        except: pass

    return alerts

def log_security_event(user_id, action, details):
    # 1. Local SQLite (Sync)
    db = get_db()
    db.execute("INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)", 
               (user_id, action, details))
    db.commit()
    
    # 2. Firebase Cloud (Async/Hybrid)
    firebase_handler.log_event_fb(user_id, action, details)

# Track failed logins
failed_login_attempts = {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        print(f"DEBUG: Login Attempt for user: {username}")
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if username not in failed_login_attempts: failed_login_attempts[username] = []
        now = datetime.datetime.now()
        failed_login_attempts[username] = [t for t in failed_login_attempts[username] if (now - t).total_seconds() < 300]

        if user and check_password_hash(user['password'], password):
            print("DEBUG: Password Correct")
            if user['access_revoked']:
                return jsonify({'error': 'ACCESS DENIED: Account revoked.'}), 403
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['login_time'] = datetime.datetime.now().isoformat()
            failed_login_attempts[username] = []
            
            log_security_event(user['id'], 'LOGIN', f"User {username} logged in from {request.remote_addr}")
            alerts = check_anomaly(user['id'], username)
            return jsonify({'success': True, 'redirect': '/dashboard', 'alerts': alerts})
        else:
            failed_login_attempts[username].append(now)
            count = len(failed_login_attempts[username])
            if user: log_security_event(user['id'], 'LOGIN_FAIL', f"Failed login {count}/5")
            print(f"DEBUG: Invalid Credentials for {username}")
            if count >= 3 and user:
                log_security_event(user['id'], 'SECURITY_ALERT', f"Brute force detected: {count} fails")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if not user or user['access_revoked']:
        session.clear()
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=user)

@app.route('/api/stats')
def api_stats():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'cpu': random.randint(10, 90),
        'network': random.randint(100, 5000), 
        'threat_level': 'HIGH' if len(failed_login_attempts.get(session.get('username'), [])) > 0 else 'LOW'
    })

# Registration & Verification
verification_codes = {}
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    db = get_db()
    if db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
        return jsonify({'error': 'Username exists'}), 400
    code = ''.join(random.choices(string.digits, k=6))
    verification_codes[email] = {'code': code, 'data': {'username': username, 'password': generate_password_hash(password), 'role': 'user'}}
    print(f"\n[SIMULATED EMAIL] Code: {code}\n")
    return jsonify({'success': True, 'simulation_code': code})

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    if email not in verification_codes or verification_codes[email]['code'] != code:
        return jsonify({'error': 'Invalid code'}), 400
    user_data = verification_codes[email]['data']
    db = get_db()
    db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
               (user_data['username'], user_data['password'], user_data['role']))
    db.commit()
    del verification_codes[email]
    return jsonify({'success': True})

# File Upload & Analysis
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    log_security_event(session['user_id'], 'FILE_UPLOAD', f"Uploaded file: {filename}")
    
    # Analyze
    graph_data = {'activity_by_hour': [0]*24, 'data_by_user': {}, 'incidents': []}
    scan_result = "CLEAN"
    
    try:
        content = file.read().decode('utf-8', errors='ignore')
        lines = content.splitlines()
        reader = csv.reader(lines)
        headers = next(reader, None)
        
        # Heuristic to find columns
        def get_val(row, heads, keys):
            if not heads: return None
            for k in keys:
                for i, h in enumerate(heads):
                    if k in h.lower(): return row[i] if i < len(row) else None
            return None

        for row in reader:
            if not row: continue
            
            # Map columns based on User's format: Timestamp,User_ID,Activity,Details,Status,Bytes_Transferred
            # using the existing helper to be flexible but prioritizing the requested names
            ts_str = get_val(row, headers, ['timestamp', 'time', 'date'])
            user = get_val(row, headers, ['user_id', 'user', 'source']) or 'Unknown'
            activity = get_val(row, headers, ['activity', 'action']) or 'Event'
            details = get_val(row, headers, ['details', 'info']) or ''
            status = get_val(row, headers, ['status', 'state']) or 'Unknown'
            bytes_str = get_val(row, headers, ['bytes_transferred', 'bytes', 'size'])
            
            row_text = str(row).lower()
            score = 0
            anomalies = []

            # 1. After-hours login (Time Anomaly)
            if ts_str:
                try:
                    parts = ts_str.replace('T', ' ').split(' ')
                    time_part = parts[1] if len(parts) > 1 else parts[0]
                    hour = int(time_part.split(':')[0])
                    if 0 <= hour < 24: 
                        graph_data['activity_by_hour'][hour] += 1
                        if hour < 7 or hour > 19:
                             score += 3
                             anomalies.append('After-hours Login')
                except: pass
            
            # 2. Large Data Copy / External Transfer (Bytes Anomaly)
            if bytes_str:
                try:
                    mb = int(bytes_str) / 1024 / 1024
                    if user: graph_data['data_by_user'][user] = graph_data['data_by_user'].get(user, 0) + mb
                    
                    if mb > 100: # Increased threshold for "Large"
                        score += 6
                        anomalies.append(f'Large Data Transfer ({int(mb)}MB)')
                        
                    if 'copy' in activity.lower() and mb > 50:
                        score += 5
                        anomalies.append('Large Data Copy')
                except: pass

            # 3. Explicit Keyword Matching for Requested Threats
            
            # Unfamiliar IP
            if 'unfamiliar ip' in row_text or 'unknown ip' in row_text or 'new location' in row_text:
                score += 8; anomalies.append('Unfamiliar IP Login')

            # USB Insertion
            if 'usb' in row_text or 'removable' in row_text or 'flash drive' in row_text:
                score += 7; anomalies.append('USB Insertion')

            # External Data Transfer
            if 'external' in row_text or 'exfiltration' in row_text:
                score += 8; anomalies.append('External Data Transfer')
                
            # Disguised Executable
            if 'disguised' in row_text or 'double extension' in row_text or '.jpg.exe' in row_text:
                score += 10; anomalies.append('Disguised Executable')

            # Log Deletion
            if 'deletion' in row_text or 'delete log' in row_text or 'clear event' in row_text:
                score += 10; anomalies.append('Log Deletion')
                
            # Unauthorized Data Access
            if 'unauthorized' in row_text or 'access denied' in row_text or 'denied' in status.lower():
                score += 7; anomalies.append('Unauthorized Access')

            # File Renaming Disguise
            if 'rename' in row_text and ('disguise' in row_text or 'hidden' in row_text):
                score += 8; anomalies.append('File Renaming Disguise')
            elif 'rename' in row_text: # weak signal
                score += 2
                
            # Cloud Upload
            if 'upload' in row_text or 'cloud' in row_text or 'gdrive' in row_text or 'dropbox' in row_text:
                score += 6; anomalies.append('Cloud Upload')
                
            # Brute-force Login
            if 'brute' in row_text or ('fail' in row_text and 'multiple' in row_text):
                score += 9; anomalies.append('Brute-force Login')
                
            # Autorun Persistence
            if 'autorun' in row_text or 'persistence' in row_text or 'registry' in row_text or 'startup' in row_text:
                score += 9; anomalies.append('Autorun Persistence')
                
            # Hidden File Metadata
            if 'hidden' in row_text or 'metadata' in row_text or 'stream' in row_text:
                score += 7; anomalies.append('Hidden Metadata')
            
            # Deduplicate and Record
            if anomalies:
                # Ensure unique
                seen = set()
                uniq_anomalies = [x for x in anomalies if not (x in seen or seen.add(x))]
                
                graph_data['incidents'].append({
                    'score': score, 
                    'timestamp': ts_str or 'N/A', 
                    'user_id': user, 
                    'activity': activity, 
                    'anomalies': ', '.join(uniq_anomalies), 
                    'details': details or activity
                })
                scan_result = "THREATS FOUND"
    except Exception as e:
        print(f"Parse Error: {e}")
        scan_result = "ERROR"

    # Mock data if empty
    if sum(graph_data['activity_by_hour']) == 0:
        graph_data['activity_by_hour'] = [0,2,5,3,1,0,0,0,0,30,51,32,35,26,38,4,0,0,0,0,0,0,0,0]
    if not graph_data['data_by_user']:
        graph_data['data_by_user'] = {'UserA': 500, 'UserB': 200}
        
    # --- Persistence Update: Save findings to DB so they appear in Dashboard/Report ---
    if graph_data['incidents']:
        db = get_db()
        # count existing anomalies to avoid flooding if re-uploading (simple check)
        existing_count = db.execute("SELECT COUNT(*) FROM logs WHERE action = 'SECURITY_ANOMALY'").fetchone()[0]
        
        if existing_count < 50: # Limit to avoid DB explosion in demo
            for inc in graph_data['incidents']:
                # Attribute to the admin running the scan, but detail the specific threat
                # Action must contain 'ANOMALY' to be picked up by frontend filter
                db.execute("INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)",
                           (session['user_id'], 'SECURITY_ANOMALY', f"[{inc['user_id']}] {inc['anomalies']}"))
            db.commit()
            
    return jsonify({
        'success': True, 'scan_result': scan_result, 'graph_data': graph_data
    })

@app.route('/api/items') # Placeholder to prevent 404 if frontend calls it
def items(): return jsonify([])

@app.route('/api/logs')
def get_logs():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    logs = db.execute("SELECT l.id, l.timestamp, u.username, l.action, l.details FROM logs l JOIN users u ON l.user_id = u.id ORDER BY l.timestamp DESC LIMIT 50").fetchall()
    return jsonify([dict(row) for row in logs])

# --- MDM FEATURES ---

@app.route('/api/devices')
def get_devices():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    devices = db.execute("SELECT * FROM devices").fetchall()
    return jsonify([dict(row) for row in devices])

@app.route('/api/mdm/enroll', methods=['POST'])
def mdm_enroll():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    import uuid
    token = str(uuid.uuid4())
    # Return mock QR info
    return jsonify({
        'success': True,
        'enrollment_link': f"https://mdm.garuda.sec/enroll/{token}",
        'qr_data': token 
    })

@app.route('/api/mdm/new_device_simulate', methods=['POST'])
def mdm_new_device():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    name = request.json.get('name', 'New Device')
    dtype = request.json.get('type', 'Mobile')
    db = get_db()
    cursor = db.execute("INSERT INTO devices (user_id, device_name, device_type, status, last_seen) VALUES (?, ?, ?, ?, ?)",
               (session['user_id'], name, dtype, 'Provisioning', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    db.commit()
    log_security_event(session['user_id'], 'DEVICE_ENROLL', f"Enrolled {dtype}: {name} (ID: {cursor.lastrowid})")
    return jsonify({'success': True})

@app.route('/api/mdm/command', methods=['POST'])
def mdm_command():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    
    cmd = request.json.get('command') # lock, wipe, encrypt, isolate, scan, revoke
    device_id = request.json.get('device_id')
    db = get_db()
    
    log_msg = f"MDM Command '{cmd.upper()}' sent to Device ID {device_id}"
    
    if cmd == 'lock':
        db.execute("UPDATE devices SET is_locked = 1, status = 'Locked' WHERE id = ?", (device_id,))
    elif cmd == 'unlock':
        db.execute("UPDATE devices SET is_locked = 0, status = 'Secure' WHERE id = ?", (device_id,))
    elif cmd == 'wipe':
        db.execute("UPDATE devices SET status = 'Wiped/Reset', is_locked=0, is_encrypted=0 WHERE id = ?", (device_id,))
        log_msg += " - Device Factory Reset Initiated"
    elif cmd == 'encrypt':
        db.execute("UPDATE devices SET is_encrypted = 1 WHERE id = ?", (device_id,))
    elif cmd == 'isolate':
        db.execute("UPDATE devices SET is_isolated = 1, status = 'Isolated' WHERE id = ?", (device_id,))
    elif cmd == 'scan':
        import random
        threat_found = random.choice([True, False])
        new_status = 'Compromised' if threat_found else 'Secure'
        risk = 90 if threat_found else 0
        db.execute("UPDATE devices SET status = ?, risk_score = ? WHERE id = ?", (new_status, risk, device_id))
        log_msg = f"MDM Scan: {new_status.upper()}"
        if threat_found: log_security_event(session['user_id'], 'THREAT_DETECTED', f"Malware signature on Device {device_id}")

    elif cmd == 'revoke':
        dev = db.execute("SELECT user_id FROM devices WHERE id = ?", (device_id,)).fetchone()
        if dev:
            db.execute("UPDATE users SET access_revoked = 1 WHERE id = ?", (dev['user_id'],))
            db.execute("UPDATE devices SET status = 'Revoked' WHERE id = ?", (device_id,))
            log_msg += " (User Access Revoked)"

    log_security_event(session['user_id'], 'MDM_ACTION', log_msg)
    
    # --- FIREBASE SYNC ---
    # Push command to cloud for Agent pickup
    firebase_handler.send_device_command_fb(device_id, cmd)
    firebase_handler.sync_device_state_fb(device_id, {'status': 'Command Sent', 'last_cmd': cmd})
    
    return jsonify({'success': True, 'message': f"Command {cmd.upper()} executed."})

# Legacy security ops
@app.route('/api/security/revoke', methods=['POST'])
def revoke_access():
    target_user = request.json.get('username')
    db = get_db()
    db.execute("UPDATE users SET access_revoked = 1 WHERE username = ?", (target_user,))
    db.commit()
    log_security_event(session['user_id'], 'RESPONSE_OP', f"Access Revoked for {target_user}")
    return jsonify({'success': True, 'message': f"Access Revoked for {target_user}"})

@app.route('/api/security/encrypt', methods=['POST'])
def encrypt_exfiltration():
    log_security_event(session['user_id'], 'RESPONSE_OP', "global_encryption_protocol_initiated")
    return jsonify({'success': True, 'message': "Data lock active."})

@app.route('/api/security/isolate', methods=['POST'])
def isolate_user():
    log_security_event(session['user_id'], 'RESPONSE_OP', "node_isolation_confirmed")
    return jsonify({'success': True, 'message': "User isolated."})

@app.route('/api/security/soc_alert', methods=['POST'])
def soc_alert():
    log_security_event(session['user_id'], 'SOC_ALERT', "CRITICAL: Manual SOC Broadcast Triggered by Admin")
    return jsonify({'success': True, 'message': "SOC Notified. Incident #9921 Created."})

if __name__ == '__main__':
    if not os.path.exists('uploads'): os.makedirs('uploads')
    init_db()
    app.run(debug=True, port=5000)
