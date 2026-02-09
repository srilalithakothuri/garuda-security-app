# How to Enable Firebase Integration 🚀
To make your "Response Actions" (Isolate, Wipe, Encrypt) work in real-time across the internet, you need to add your Firebase credentials.

### Step 1: Get your Key file
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Select your project (or create one).
3. Go to **Project Settings** (gear icon) -> **Service accounts**.
4. Click **Generate new private key**.
5. Save the file and rename it to `serviceAccountKey.json`.

### Step 2: Place the file
Move the `serviceAccountKey.json` file into this specific folder:
`C:\Users\kothu\.gemini\antigravity\scratch\security_app\`

### Step 3: Enable Database
1. In Firebase Console, go to **Build** -> **Realtime Database**.
2. Click **Create Database** (start in Test Mode for now).
3. Copy the database URL (it starts with `https://...` and ends with `firebaseio.com`).
4. Open `firebase_handler.py` in this folder.
5. Replace `https://YOUR_PROJECT_ID.firebaseio.com/` with your actual URL.

### Done!
Restart the app. You will see `[SUCCESS] Connected to Firebase` in the terminal. Now, every time you click "Isolate Device" or "Revoke Access", the command is sent to the cloud instantly!
