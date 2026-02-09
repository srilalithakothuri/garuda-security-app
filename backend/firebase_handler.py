import firebase_admin
from firebase_admin import credentials, firestore, db as realtime_db
import os
import datetime

# --- CONFIGURATION ---
# You must place your 'serviceAccountKey.json' in the same folder as this file.
KEY_PATH = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
# Auto-configured based on your key file
FIREBASE_DB_URL = 'https://garuda-d9ad4-default-rtdb.firebaseio.com/'

_firestore_client = None
_is_initialized = False

def init_firebase():
    global _firestore_client, _is_initialized
    if _is_initialized: return True
    
    if not os.path.exists(KEY_PATH):
        print(f"[WARNING] Firebase Key not found at {KEY_PATH}. Running in Local-Only mode.")
        return False

    try:
        cred = credentials.Certificate(KEY_PATH)
        # We initialize with options for Realtime DB access
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL
        })
        _firestore_client = firestore.client()
        _is_initialized = True
        print("[SUCCESS] Connected to Firebase.")
        return True
    except Exception as e:
        print(f"[ERROR] Firebase Init Failed: {e}")
        return False

# --- LOGGING ---
def log_event_fb(user_id, action, details):
    if not _is_initialized: return
    try:
        # 1. Store in Firestore for history/reporting
        data = {
            'user_id': user_id,
            'action': action,
            'details': details,
            'timestamp': datetime.datetime.now().isoformat()
        }
        _firestore_client.collection('security_logs').add(data)
        
        # 2. Update 'Latest Alert' in Realtime DB for Dashboard widgets
        # 2. Update 'latest_logs' in Realtime DB so it shows up instantly in the Console
        # We push ALL events now so you can see them (Uploads, Logins, etc.)
        realtime_db.reference('latest_logs').push(data)
        
        if "ALERT" in action or "ANOMALY" in action:
            realtime_db.reference('live_alerts').push(data)
            
    except Exception as e:
        print(f"FB Log Error: {e}")

# --- DEVICE MONITORING (Command & Control) ---
def send_device_command_fb(device_id, command):
    if not _is_initialized: return False
    try:
        # Write command to a specific device node that an Agent would listen to
        # Node: /devices/{device_id}/commands
        cmd_data = {
            'command': command,
            'issued_at': datetime.datetime.now().isoformat(),
            'status': 'PENDING'
        }
        ref = realtime_db.reference(f'devices/{device_id}/commands').push(cmd_data)
        return True
    except Exception as e:
        print(f"FB Command Error: {e}")
        return False

def sync_device_state_fb(device_id, state_data):
    if not _is_initialized: return
    try:
        realtime_db.reference(f'devices/{device_id}/status').set(state_data)
    except: pass
