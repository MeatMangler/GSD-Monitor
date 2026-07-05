#Requires -Version 5.1
<#
.SYNOPSIS
    GSD Monitor Installer - bootstraps a full installation from nothing.

.DESCRIPTION
    Checks prerequisites (Git, Python 3.11+, Node.js, WebView2), clones the
    GSD Monitor repository, creates a Python virtual environment, installs
    dependencies, builds the React frontend, writes a start.bat launcher, and
    creates a desktop shortcut.  Running the script a second time on an
    existing installation offers an upgrade (git pull + rebuild) instead of
    re-cloning.

.PARAMETER InstallPath
    Override the default installation directory.
    Default: %LOCALAPPDATA%\GSDMonitor

.PARAMETER NoWait
    Skip the final "Press Enter to exit" pause.  Useful for scripted/
    non-interactive invocations.

.EXAMPLE
    iex (irm https://raw.githubusercontent.com/MeatMangler/GSD-Monitor/master/install.ps1)

.EXAMPLE
    powershell -File install.ps1 -InstallPath "$env:TEMP\GSDMonitorTest" -NoWait
#>
[CmdletBinding()]
param(
    [string]$InstallPath,
    [switch]$NoWait
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

function Write-Step {
    param([string]$msg)
    Write-Host "`n>> $msg" -ForegroundColor Cyan
}

function Write-OK {
    param([string]$msg)
    Write-Host "   OK: $msg" -ForegroundColor Green
}

function Fail {
    param([string]$msg)
    Write-Host "`nERROR: $msg" -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "======================================" -ForegroundColor White
Write-Host "   GSD Monitor Installer              " -ForegroundColor White
Write-Host "======================================" -ForegroundColor White
Write-Host ""

# ---------------------------------------------------------------------------
# Section 1 - Prerequisite checks (all upfront, before any mutation)
# ---------------------------------------------------------------------------

Write-Step "Checking prerequisites..."

# Git
try { $gitVer = git --version 2>&1 } catch { $gitVer = $null }
if ($LASTEXITCODE -ne 0 -or -not $gitVer) {
    Fail "Git not found.`nDownload from: https://git-scm.com/download/win"
}
Write-OK "Git: $gitVer"

# Python 3.11+
try { $pyVer = python --version 2>&1 } catch { $pyVer = $null }
if ($LASTEXITCODE -ne 0 -or -not $pyVer) {
    Fail "Python not found.`nDownload from: https://www.python.org/downloads/"
}
if ($pyVer -match 'Python (\d+)\.(\d+)') {
    $maj = [int]$Matches[1]
    $min = [int]$Matches[2]
    if ($maj -lt 3 -or ($maj -eq 3 -and $min -lt 11)) {
        Fail "Python 3.11+ required (found $pyVer).`nDownload from: https://www.python.org/downloads/"
    }
} else {
    Fail "Could not parse Python version from: $pyVer`nDownload from: https://www.python.org/downloads/"
}
Write-OK "Python: $pyVer"

# Node.js
try { $nodeVer = node --version 2>&1 } catch { $nodeVer = $null }
if ($LASTEXITCODE -ne 0 -or -not $nodeVer) {
    Fail "Node.js not found.`nDownload from: https://nodejs.org/"
}
Write-OK "Node.js: $nodeVer"

# WebView2 - check both HKLM and HKCU (Evergreen installer may use either)
$wv2Key   = 'F3017226-FE2A-4295-8BDF-00C3A9A7E4C5'
$wv2Paths = @(
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{$wv2Key}",
    "HKCU:\Software\Microsoft\EdgeUpdate\Clients\{$wv2Key}"
)
$wv2OK = $false
foreach ($p in $wv2Paths) {
    $pv = (Get-ItemProperty $p -ErrorAction SilentlyContinue).pv
    if ($pv -and $pv -ne '' -and $pv -ne '0.0.0.0') {
        $wv2OK = $true
        break
    }
}
if (-not $wv2OK) {
    Fail "Microsoft Edge WebView2 Runtime not found.`nDownload from: https://developer.microsoft.com/microsoft-edge/webview2/consumer/"
}
Write-OK "WebView2 Runtime: present"

# ---------------------------------------------------------------------------
# Section 2 - Install path resolution
# ---------------------------------------------------------------------------

Write-Step "Resolving installation directory..."

$defaultPath = Join-Path $env:LOCALAPPDATA 'GSDMonitor'

if ($InstallPath) {
    $installDir = $InstallPath.Trim()
} else {
    $inputPath = Read-Host "Install directory [$defaultPath]"
    $installDir = if ($inputPath.Trim() -eq '') { $defaultPath } else { $inputPath.Trim() }
}

# Security: reject UNC paths and paths containing '..' segments
if ($installDir -match '^\\\\') {
    Fail "UNC paths are not supported as an install directory: $installDir"
}
if ($installDir -match '\.\.') {
    Fail "Install path must not contain '..' segments: $installDir"
}

# Resolve to absolute path
$installDir = [System.IO.Path]::GetFullPath($installDir)

Write-Host "   Installing to: $installDir" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# Section 3 - Upgrade detection
# ---------------------------------------------------------------------------

if (Test-Path (Join-Path $installDir '.git')) {
    Write-Host "`nExisting GSD Monitor installation found at: $installDir" -ForegroundColor Yellow

    $currentHash = git -C $installDir log --oneline -1 2>$null
    git -C $installDir fetch origin --quiet 2>$null
    $remoteHash  = git -C $installDir log --oneline -1 origin/master 2>$null

    Write-Host "  Current: $currentHash"
    Write-Host "  Latest:  $remoteHash"

    $answer = Read-Host "`nUpgrade GSD Monitor? [Y/n]"
    if ($answer -match '^[Nn]') {
        Write-Host "No changes made." -ForegroundColor Yellow
        exit 0
    }

    Write-Step "Pulling latest changes..."
    git -C $installDir pull
    if ($LASTEXITCODE -ne 0) { Fail "git pull failed - installation unchanged" }
    Write-OK "Repository updated"

    Write-Step "Re-installing Python dependencies..."
    & "$installDir\.venv\Scripts\pip.exe" install `
        fastapi "uvicorn[standard]" pydantic pydantic-settings pywebview pygit2 watchdog
    if ($LASTEXITCODE -ne 0) { Fail "pip install failed during upgrade" }
    Write-OK "Python dependencies up to date"

    Write-Step "Rebuilding frontend..."
    Push-Location (Join-Path $installDir 'frontend')
    npm install
    if ($LASTEXITCODE -ne 0) { Pop-Location; Fail "npm install failed during upgrade" }
    npm run build
    if ($LASTEXITCODE -ne 0) { Pop-Location; Fail "npm run build failed during upgrade" }
    Pop-Location
    Write-OK "Frontend rebuilt"

    Write-Host "`nUpgrade complete." -ForegroundColor Green
    exit 0
}

# ---------------------------------------------------------------------------
# Section 4 - Fresh install
# ---------------------------------------------------------------------------

$repoUrl = 'https://github.com/MeatMangler/GSD-Monitor.git'

Write-Step "Cloning GSD Monitor repository..."
git clone $repoUrl $installDir
if ($LASTEXITCODE -ne 0) { Fail "git clone failed" }
Write-OK "Repository cloned to $installDir"

Write-Step "Creating Python virtual environment..."
python -m venv "$installDir\.venv"
if ($LASTEXITCODE -ne 0) { Fail "Failed to create virtual environment" }
Write-OK "Virtual environment created"

Write-Step "Installing Python dependencies..."
& "$installDir\.venv\Scripts\pip.exe" install `
    fastapi "uvicorn[standard]" pydantic pydantic-settings pywebview pygit2 watchdog
if ($LASTEXITCODE -ne 0) { Fail "pip install failed" }
Write-OK "Python dependencies installed"

Write-Step "Building frontend (npm install + npm run build)..."
Push-Location (Join-Path $installDir 'frontend')
npm install
if ($LASTEXITCODE -ne 0) { Pop-Location; Fail "npm install failed" }
npm run build
if ($LASTEXITCODE -ne 0) { Pop-Location; Fail "npm run build failed" }
Pop-Location
Write-OK "Frontend built"

# ---------------------------------------------------------------------------
# Section 5 - Launcher creation (start.bat)
# ---------------------------------------------------------------------------

Write-Step "Writing start.bat launcher..."
$batContent = @"
@echo off
setlocal
cd /d "%~dp0"

:: Auto-update -- check for newer commits on origin/master
git fetch origin master >nul 2>&1
if errorlevel 1 goto launch

for /f %%h in ('git rev-parse HEAD 2^>nul') do set _cur=%%h
for /f %%h in ('git rev-parse origin/master 2^>nul') do set _new=%%h

if not defined _new goto launch
if /i "%_cur%"=="%_new%" goto launch

echo.
echo Updating GSD Monitor...
git pull --ff-only
if errorlevel 1 goto launch
.venv\Scripts\pip.exe install -q fastapi "uvicorn[standard]" pydantic pydantic-settings pywebview pygit2 watchdog
if errorlevel 1 goto launch
pushd frontend
npm install --silent 2>nul
npm run build --silent 2>nul
popd
echo Update complete.
timeout /t 2 /nobreak >nul

:launch
start "" /b .venv\Scripts\pythonw.exe -m gsd_monitor
"@
Set-Content -Path (Join-Path $installDir 'start.bat') -Value $batContent -Encoding ASCII
Write-OK "start.bat written"

# ---------------------------------------------------------------------------
# Section 6 - Desktop shortcut
# ---------------------------------------------------------------------------

Write-Step "Creating desktop shortcut..."
$desktopPath   = [Environment]::GetFolderPath('Desktop')
$shortcutLabel = if ($installDir -eq $defaultPath) { 'Start GSD Monitor' } else { "Start GSD Monitor ($installDir)" }
$shortcutPath  = Join-Path $desktopPath "$shortcutLabel.lnk"
$iconPath      = Join-Path $installDir 'assets\gsd-icon.ico'

$shell = New-Object -ComObject 'WScript.Shell'
$lnk   = $shell.CreateShortcut($shortcutPath)
$lnk.TargetPath       = Join-Path $installDir 'start.bat'
$lnk.WorkingDirectory = $installDir
$lnk.Description      = 'GSD Monitor - project status dashboard'
$lnk.WindowStyle      = 7   # minimised - the bat window should not stay visible; pywebview is the real UI
if (Test-Path $iconPath) {
    $lnk.IconLocation = "$iconPath, 0"
}
$lnk.Save()
Write-OK "Desktop shortcut created: '$shortcutLabel'"

# ---------------------------------------------------------------------------
# Section 7 - Success message
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "   GSD Monitor installed successfully!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "   Location : $installDir" -ForegroundColor White
Write-Host "   Launch   : Use the '$shortcutLabel' desktop shortcut" -ForegroundColor White
Write-Host "           or run: $installDir\start.bat" -ForegroundColor White
Write-Host ""

if (-not $NoWait) {
    Read-Host "Press Enter to exit"
}
