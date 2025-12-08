# PowerShell script to help set up GitHub repository
# Run this script in PowerShell: .\setup_github.ps1

Write-Host "=== CertChain GitHub Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
try {
    $gitVersion = git --version
    Write-Host "✓ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Or run: winget install Git.Git" -ForegroundColor Yellow
    exit 1
}

# Check if already a git repository
if (Test-Path .git) {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
} else {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
}

# Check for sensitive data
Write-Host ""
Write-Host "Checking for sensitive data..." -ForegroundColor Yellow
$settingsFile = "core\settings.py"
if (Test-Path $settingsFile) {
    $content = Get-Content $settingsFile -Raw
    if ($content -match "EMAIL_HOST_PASSWORD\s*=\s*['""][^'""]+['""]") {
        Write-Host "⚠ WARNING: Hardcoded email password found in settings.py!" -ForegroundColor Red
        Write-Host "  Please remove it before committing to GitHub." -ForegroundColor Yellow
        Write-Host "  Use environment variables instead (see .env.example)" -ForegroundColor Yellow
    } else {
        Write-Host "✓ No hardcoded passwords found" -ForegroundColor Green
    }
}

# Check if .env file exists
if (Test-Path .env) {
    Write-Host "✓ .env file exists (will be ignored by git)" -ForegroundColor Green
} else {
    Write-Host "ℹ .env file not found (create one from .env.example)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Review and remove sensitive data from core/settings.py" -ForegroundColor White
Write-Host "2. Create .env file from .env.example template" -ForegroundColor White
Write-Host "3. Run: git add ." -ForegroundColor White
Write-Host "4. Run: git commit -m 'Initial commit'" -ForegroundColor White
Write-Host "5. Create repository on GitHub: https://github.com/new" -ForegroundColor White
Write-Host "6. Run: git remote add origin https://github.com/YOUR_USERNAME/CertChain.git" -ForegroundColor White
Write-Host "7. Run: git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see GITHUB_SETUP.md" -ForegroundColor Cyan

