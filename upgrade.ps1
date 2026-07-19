#Requires -Version 5.1
<#
.SYNOPSIS
    GSD Monitor Upgrade - updates an existing installation to the latest version.

.DESCRIPTION
    Validates that the script is run from a valid GSD Monitor installation directory,
    checks for available updates via git fetch, and if newer commits exist: pulls them,
    reinstalls Python dependencies via pip install -e ., and rebuilds the React frontend.
    Exits cleanly with an informational message if already up to date.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File upgrade.ps1

.EXAMPLE
    .\upgrade.bat
#>

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

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
Write-Host "   GSD Monitor Upgrade               " -ForegroundColor White
Write-Host "======================================" -ForegroundColor White
Write-Host ""

# ---------------------------------------------------------------------------
# Section 1 - Valid-install guard (UPG-02)
# ---------------------------------------------------------------------------

$root = $PSScriptRoot

if (-not (Test-Path (Join-Path $root 'gsd_monitor'))) {
    Fail "This script must be run from a valid GSD Monitor installation directory. Expected 'gsd_monitor' folder not found in: $root"
}

if (-not (Test-Path (Join-Path $root '.venv\Scripts\pip.exe'))) {
    Fail "Virtual environment not found. Expected '.venv\Scripts\pip.exe' in: $root. Run install.ps1 first."
}

# ---------------------------------------------------------------------------
# Section 2 - Fetch and compare (UPG-03)
# ---------------------------------------------------------------------------

Write-Step "Checking for updates..."
git -C $root fetch origin master --quiet
if ($LASTEXITCODE -ne 0) {
    Fail "Could not reach remote repository. Check your internet connection."
}

$localHash  = git -C $root rev-parse HEAD
$remoteHash = git -C $root rev-parse origin/master

if ($localHash -eq $remoteHash) {
    Write-Host "`nAlready up to date. Nothing to do." -ForegroundColor Green
    exit 0
}

# ---------------------------------------------------------------------------
# Section 3 - Pull
# ---------------------------------------------------------------------------

Write-Step "Pulling latest changes..."
git -C $root pull origin master
if ($LASTEXITCODE -ne 0) {
    Fail "git pull failed. You may have local changes — commit or stash them first."
}
Write-OK "Repository updated"

# ---------------------------------------------------------------------------
# Section 4 - pip install
# ---------------------------------------------------------------------------

Write-Step "Updating Python dependencies..."
& (Join-Path $root '.venv\Scripts\pip.exe') install -e "$root"
if ($LASTEXITCODE -ne 0) {
    Fail "pip install failed"
}
Write-OK "Dependencies updated"

# ---------------------------------------------------------------------------
# Section 5 - Frontend rebuild
# ---------------------------------------------------------------------------

Write-Step "Rebuilding frontend..."
Push-Location (Join-Path $root 'frontend')
npm ci
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Fail "npm ci failed"
}
npm run build
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Fail "npm run build failed"
}
Pop-Location
Write-OK "Frontend rebuilt"

# ---------------------------------------------------------------------------
# Section 6 - Success
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "   Upgrade complete.                 " -ForegroundColor Green
Write-Host "   Run start.bat to launch.          " -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
