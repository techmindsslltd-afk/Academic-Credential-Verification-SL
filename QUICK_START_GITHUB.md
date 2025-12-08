# Quick Start: Upload to GitHub

## ⚠️ IMPORTANT: Remove Sensitive Data First!

Before uploading, you **MUST** remove the hardcoded email password from `core/settings.py` (line 382).

**Current (UNSAFE):**
```python
EMAIL_HOST_PASSWORD = 'hcerpjroveukllar'  # Remove this!
```

**Should be:**
```python
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
```

Then create a `.env` file with:
```
EMAIL_HOST_PASSWORD=hcerpjroveukllar
```

## Quick Commands

### Option 1: Using PowerShell (Recommended)

```powershell
# Run the setup script
.\setup_github.ps1

# Then follow the prompts or run manually:
git init
git add .
git commit -m "Initial commit: CertChain"
```

### Option 2: Manual Steps

```bash
# 1. Install Git (if needed)
# Download from: https://git-scm.com/download/win

# 2. Initialize repository
git init

# 3. Configure your identity
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 4. Add files
git add .

# 5. Commit
git commit -m "Initial commit: CertChain - Blockchain Academic Credential Verification System"

# 6. Create repository on GitHub: https://github.com/new
#    (Don't initialize with README, .gitignore, or license)

# 7. Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/CertChain.git
git branch -M main
git push -u origin main
```

## What's Already Protected

✅ Database files (db.sqlite3) - excluded  
✅ Log files (*.log) - excluded  
✅ Media files - excluded  
✅ Environment files (.env) - excluded  
✅ Python cache (__pycache__) - excluded  
✅ Node modules - excluded  

## Need Help?

See `GITHUB_SETUP.md` for detailed instructions.

