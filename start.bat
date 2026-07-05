@echo off
setlocal
cd /d "%~dp0"

:: ── Auto-update ──────────────────────────────────────────────────────────────
where git >nul 2>&1
if errorlevel 1 (
    echo WARNING: git not found on PATH - skipping update check.
    echo Install Git from https://git-scm.com or add it to PATH.
    timeout /t 4 /nobreak >nul
    goto launch
)

echo Checking for updates...
git fetch origin master --quiet
if errorlevel 1 (
    echo WARNING: Could not reach GitHub to check for updates - launching existing version.
    timeout /t 3 /nobreak >nul
    goto launch
)

for /f %%h in ('git rev-parse HEAD 2^>nul') do set _cur=%%h
for /f %%h in ('git rev-parse origin/master 2^>nul') do set _new=%%h

if not defined _new goto launch
if /i "%_cur%"=="%_new%" goto launch

echo Update available - updating now...
git reset --hard origin/master
if errorlevel 1 (
    echo ERROR: git reset failed - launching existing version.
    timeout /t 5 /nobreak >nul
    goto launch
)

echo Installing Python dependencies...
.venv\Scripts\pip.exe install -q fastapi "uvicorn[standard]" pydantic pydantic-settings pywebview pygit2 watchdog
if errorlevel 1 (
    echo ERROR: pip install failed - launching existing version.
    timeout /t 5 /nobreak >nul
    goto launch
)

echo Building frontend...
pushd frontend
npm install --silent
if errorlevel 1 (
    popd
    echo ERROR: npm install failed - launching existing version.
    timeout /t 5 /nobreak >nul
    goto launch
)
npm run build
if errorlevel 1 (
    popd
    echo ERROR: npm build failed - launching existing version.
    timeout /t 5 /nobreak >nul
    goto launch
)
popd
echo Update complete.
timeout /t 2 /nobreak >nul

:launch
start "" /b .venv\Scripts\pythonw.exe -m gsd_monitor
