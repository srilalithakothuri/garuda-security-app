# How to Push Your Project to GitHub

Follow these steps to upload your project to your GitHub profile.

## 1. Prepare Your Local Repository
Open your terminal (PowerShell or Command Prompt) and navigate to your project directory.

### Initialize Git
Run the following command to start tracking changes with Git:
```powershell
git init
```

### Commit Your Files
Add all files to the staging area and make your first commit:
```powershell
git add .
git commit -m "Initial commit: Reorganized frontend and backend structure"
```
> [!IMPORTANT]
> Files like `serviceAccountKey.json` and `security_app.db` are automatically ignored by `.gitignore` to keep your credentials and local data private.

## 2. Create a Repository on GitHub
1. Log in to your [GitHub account](https://github.com/).
2. Click the **+** icon in the top-right corner and select **New repository**.
3. Give your repository a name (e.g., `garuda-security-app`).
4. Keep it **Public** or **Private** based on your preference.
5. **Do not** initialize the repository with a README, license, or gitignore (since we already have them locally).
6. Click **Create repository**.

## 3. Link Local to GitHub
After creating the repository, GitHub will show you a page with "Quick setup". Look for the section "push an existing repository from the command line".

Run these commands in your terminal (replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub details):
```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 4. How to Update in the Future
Whenever you make changes to the code and want to update GitHub, run:
```powershell
git add .
git commit -m "Description of what I changed"
git push
```

---

### ⚠️ A Note on Security
**Your Firebase Credentials**: Since we added `serviceAccountKey.json` to `.gitignore`, that file will **not** be pushed to GitHub. This is good for security! However, if you want to deploy this elsewhere, you will need to manually upload that file or use environment variables.
