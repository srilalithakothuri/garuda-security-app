# 🚀 How to Host "GARUDA" Publicly (Free)

The easiest way to host this Python Flask app for free is using **Render.com**. Follow these exact steps:

### Step 1: Create a GitHub Repository
1.  Go to [GitHub.com](https://github.com) and create a **New Repository** (name it `garuda-security`).
2.  Open your terminal in the `security_app` folder (where `app.py` is).
3.  Run these commands to push your code:
    ```bash
    git init
    git add .
    git commit -m "Initial deploy"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/garuda-security.git
    git push -u origin main
    ```
    *(Replace `YOUR_USERNAME` with your actual GitHub username)*

### Step 2: Deploy on Render
1.  Go to [dashboard.render.com](https://dashboard.render.com/register) and Sign Up (you can use your GitHub account).
2.  Click **"New +"** and select **"Web Service"**.
3.  Connect your GitHub account and select the `garuda-security` repository you just created.
4.  **Configure the Service:**
    *   **Name:** `garuda-app` (or unique name)
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn app:app`
5.  Scroll down and click **"Create Web Service"**.

### Step 3: Done!
*   Render will take about 1-2 minutes to build.
*   Once finished, it will give you a public URL (e.g., `https://garuda-app.onrender.com`).
*   **Share this link!** Anyone can now access your Insider Threat Dashboard.

---
**Note:** Since this uses a local SQLite database (`security_app.db`), the database will reset every time the server restarts on the free tier. For a permanent database, you would need to add a Postgres database, but for a **demo**, this file-based setup is perfect (keeps it clean).
