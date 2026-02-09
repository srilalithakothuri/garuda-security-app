import firebase_admin
from firebase_admin import credentials, db
import os
import sys

# 1. Setup
KEY_PATH = 'serviceAccountKey.json'
DB_URL = 'https://garuda-d9ad4-default-rtdb.firebaseio.com/'

print(f"Testing Connection to: {DB_URL}")

if not os.path.exists(KEY_PATH):
    print(f"ERROR: {KEY_PATH} not found in {os.getcwd()}")
    sys.exit(1)

# 2. Initialize
try:
    cred = credentials.Certificate(KEY_PATH)
    try:
        app = firebase_admin.get_app()
    except ValueError:
        app = firebase_admin.initialize_app(cred, {'databaseURL': DB_URL})
    
    print("SDK Initialized.")
except Exception as e:
    print(f"SDK Init Error: {e}")
    sys.exit(1)

# 3. Write Test
try:
    print("Attempting to write to /latest_logs...")
    ref = db.reference('latest_logs')
    ref.push({'action': 'TEST_CONNECTION', 'details': 'Forcing node creation', 'timestamp': 'NOW'})
    print("SUCCESS: Data written to /latest_logs")
except Exception as e:
    print(f"WRITE FAILED: {e}")
    # Common error: 404 if the database location is not us-central1 but the URL assumes it, 
    # or if the API is disabled.
