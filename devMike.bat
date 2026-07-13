@echo off
setlocal
cd /d "%~dp0"

echo.
echo  ============================================
echo   GSD Monitor  ^|  DEV MODE  ^|  LOCAL BUILD
echo  ============================================
echo.

:: Show what we're actually running so there's no ambiguity
for /f "delims=" %%b in ('git branch --show-current 2^>nul') do set _branch=%%b
for /f "delims=" %%h in ('git log --oneline -1 2^>nul') do set _commit=%%h
echo  Branch : %_branch%
echo  Commit : %_commit%
echo.
echo  No auto-update. No git reset. Launching local build now.
echo  Press Ctrl+C or close the app window to exit.
echo.

.venv\Scripts\python.exe -m gsd_monitor

echo.
echo  GSD Monitor exited.
pause
