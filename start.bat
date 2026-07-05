@echo off
setlocal
cd /d "%~dp0"

:: ── Auto-update ──────────────────────────────────────────────────────────────
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
