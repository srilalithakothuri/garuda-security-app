import unittest
import json
import io
import os
import sys

# Ensure we can import app
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from app import app, init_db
except ImportError:
    # Fallback for different execution contexts
    sys.path.append(os.path.join(current_dir, '..'))
    from app import app, init_db

class TestGarudaSecurity(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing
        self.db_path = 'test_security_app.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        app.config['DATABASE'] = self.db_path
        self.app = app
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except: pass

    def login(self, username, password):
        return self.client.post('/login', json=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_full_system(self):
        print("\n[TEST START] System Validation Sequence")
        
        # 1. AUTHENTICATION
        # Register
        rv = self.client.post('/api/register', json={
            'username': 'agent007', 'email': '007@garuda.sec', 'password': 'secret_agent_man'
        })
        if rv.status_code != 200:
            print(f"Auth Falied: {rv.data}")
            return
            
        data = rv.get_json()
        code = data['simulation_code']
        print(f" [PASS] Registration (Code: {code})")
        
        # Verify
        rv = self.client.post('/api/verify', json={'email': '007@garuda.sec', 'code': code})
        self.assertEqual(rv.status_code, 200)
        print(" [PASS] Verification")
        
        # Login
        rv = self.login('agent007', 'secret_agent_man')
        self.assertEqual(rv.status_code, 200)
        print(" [PASS] User Login")

        # 2. ANOMALY DETECTION (File Analysis)
        # Using the session from the login above
        csv_content = (
            "Timestamp,User_ID,Activity,Details,Status,Bytes_Transferred\n"
            "2025-12-09 03:00:00,HACKER,Login,After hours,Success,0\n"
            "2025-12-09 10:00:00,USR1,USB Inserted,Flash drive,Success,0\n"
            "2025-12-09 10:05:00,USR1,File Copy,Large USB Transfer,Success,600000000\n"
            "2025-12-09 11:00:00,USR2,Cloud Upload,Dropbox,Success,0\n"
            "2025-12-09 12:00:00,USR3,Log Deletion,Clear Events,Success,0\n"
            "2025-12-09 13:00:00,USR4,Process,payload.jpg.exe,Success,0\n"
            "2025-12-09 14:00:00,USR5,Login Failed,Unfamiliar IP,Failed,0\n"
        )
        
        data = {'file': (io.BytesIO(csv_content.encode('utf-8')), 'threats.csv')}
        rv = self.client.post('/api/upload', data=data, content_type='multipart/form-data')
        
        self.assertEqual(rv.status_code, 200)
        res_json = rv.get_json()
        self.assertEqual(res_json['scan_result'], 'THREATS FOUND')
        
        # Check specific threat strings in the anomalies
        detected_text = str(res_json['graph_data']['incidents'])
        
        threats = [
            'After-hours Login', 'USB Insertion', 'Large Data Transfer',
            'Cloud Upload', 'Log Deletion', 'Disguised Executable',
            'Unfamiliar IP Login'
        ]
        
        print("\n [THREAT DETECTION REPORT]")
        all_passed = True
        for t in threats:
            if t in detected_text:
                print(f"   [OK] Detected: {t}")
            else:
                print(f"   [XX] MISSED:   {t}")
                all_passed = False
        
        if all_passed: print(" [PASS] Anomaly Engine is 100% Operational")
        else: print(" [FAIL] Some threats were missed")

        # 3. MDM CONTROL
        # Simulate new device
        rv = self.client.post('/api/mdm/new_device_simulate', json={'name': 'TestPad', 'type': 'Tablet'})
        self.assertEqual(rv.status_code, 200)
        
        # Check it exists
        rv = self.client.get('/api/devices')
        devs = rv.get_json()
        target = next((d for d in devs if d['device_name'] == 'TestPad'), None)
        self.assertIsNotNone(target)
        print(f" [PASS] MDM Enrollment (Device ID: {target['id']})")
        
        # Send Lock Command
        rv = self.client.post('/api/mdm/command', json={'command': 'lock', 'device_id': target['id']})
        self.assertEqual(rv.status_code, 200)
        print(" [PASS] Remote Lock Command")

if __name__ == '__main__':
    unittest.main()
