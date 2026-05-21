# NEXA AI Installation Script
# Run this via: irm https://raw.githubusercontent.com/Mrcutekiller/NEXA-/main/install.ps1 | iex

$installDir = "$HOME\NEXA-AI"
$repoUrl = "https://github.com/Mrcutekiller/NEXA-.git"

Write-Host "`n[NEXA] Starting Ultimate Installation..." -ForegroundColor Magenta

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed. Please install Python 3.10+ and try again." -ForegroundColor Red
    return
}

# 2. Clone Repository
if (Test-Path $installDir) {
    Write-Host "[NEXA] Update detected. Refreshing files..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force $installDir
}

Write-Host "[NEXA] Downloading NEXA OMNI Engine..." -ForegroundColor Cyan
git clone $repoUrl $installDir

# 3. Setup Virtual Environment
Set-Location $installDir
Write-Host "[NEXA] Initializing local brain (venv)..." -ForegroundColor Cyan
python -m venv .venv

# 4. Install Dependencies
Write-Host "[NEXA] Synchronizing skills and knowledge..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

# 5. Create Execution Shortcut
$batContent = "@echo off`n`"$installDir\.venv\Scripts\python.exe`" `"$installDir\main.py`" %*"
$batPath = "$HOME\AppData\Local\Microsoft\WindowsApps\nexa.bat"
$batContent | Out-File -FilePath $batPath -Encoding ascii

Write-Host "`n[SUCCESS] NEXA AI is now installed!" -ForegroundColor Green
Write-Host "You can now start your genius companion by typing: nexa" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------`n"

# Run NEXA immediately
& nexa
