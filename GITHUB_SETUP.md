# GitHub Setup Instructions

## Prerequisites

1. **Install Git** (if not already installed):
   - Download from: https://git-scm.com/download/win
   - Or use: `winget install Git.Git` in PowerShell

2. **Create a GitHub Account** (if you don't have one):
   - Go to: https://github.com
   - Sign up for a free account

## Step-by-Step Instructions

### 1. Initialize Git Repository

Open PowerShell or Command Prompt in your project directory and run:

```bash
# Initialize git repository
git init

# Configure your git identity (replace with your info)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 2. Remove Sensitive Data from Settings

**IMPORTANT**: Before committing, you need to remove sensitive data from `core/settings.py`:

- Remove or comment out the hardcoded email password (line 382)
- Use environment variables instead (see `.env.example`)

### 3. Add Files to Git

```bash
# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status
```

### 4. Create Initial Commit

```bash
git commit -m "Initial commit: CertChain - Blockchain Academic Credential Verification System"
```

### 5. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `CertChain` (or your preferred name)
3. Description: "Blockchain Academic Credential Verification System"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

### 6. Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/CertChain.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### 7. Verify Upload

Visit your repository on GitHub to confirm all files are uploaded.

## Security Notes

⚠️ **Before pushing to GitHub, ensure:**

1. ✅ No passwords or API keys are hardcoded in settings.py
2. ✅ Database file (db.sqlite3) is excluded (already in .gitignore)
3. ✅ Media files with user data are excluded (already in .gitignore)
4. ✅ Environment variables are used for sensitive data
5. ✅ `.env` file is excluded (already in .gitignore)

## If You Need to Update Settings

1. Create a `.env` file in the project root (copy from `.env.example`)
2. Update `core/settings.py` to use `config()` from `python-decouple` for sensitive values
3. Never commit the `.env` file

## Troubleshooting

### If Git is not recognized:
- Make sure Git is installed and added to PATH
- Restart your terminal/PowerShell after installation

### If you get authentication errors:
- Use GitHub Personal Access Token instead of password
- Generate token: GitHub → Settings → Developer settings → Personal access tokens

### If you need to remove sensitive data after committing:
```bash
# Remove file from git history (use with caution)
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch core/settings.py" --prune-empty --tag-name-filter cat -- --all
```

## Next Steps

After uploading:
1. Add a comprehensive README.md
2. Add LICENSE file (if needed)
3. Set up GitHub Actions for CI/CD (optional)
4. Add collaborators (if working in a team)

