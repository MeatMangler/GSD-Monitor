---
plan: 17-02
status: complete
---

# Summary: Plan 17-02 — upgrade.ps1 + upgrade.bat

## What was done
- Created upgrade.ps1 with valid-install guard (checks gsd_monitor/ and .venv/Scripts/pip.exe)
- Fetch + hash comparison for already-up-to-date detection (exits 0 with clear message)
- git pull -> pip install -e . -> npm ci && npm run build upgrade sequence
- Created upgrade.bat as 2-line launcher: powershell -ExecutionPolicy Bypass -File upgrade.ps1

## Key decisions
- Uses git pull (not git reset --hard) -- gentler than start.bat auto-updater
- Non-interactive by design -- no Read-Host prompts
- PSScriptRoot anchors all paths so script works regardless of where it is invoked from

## Commits
- 69f06c6: feat(upgrade): add upgrade.ps1 and upgrade.bat (UPG-01-03)

## Self-Check: PASSED
- upgrade.ps1: FOUND
- upgrade.bat: FOUND
- Commit 69f06c6: FOUND
