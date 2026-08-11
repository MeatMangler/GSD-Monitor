---
plan: 17-01
status: complete
---

# Summary: Plan 17-01 — install.ps1 + pyproject.toml

## What was done
- Created pyproject.toml with hatchling build backend, all 7 runtime deps, requires-python >= 3.11
- Updated install.ps1 fresh-install section to use pip install -e "$installDir"
- Updated install.ps1 upgrade section to use pip install -e "$installDir"
- Updated start.bat template inside install.ps1 to use pip install -q -e "%~dp0."
- Verified pip install -e . works in existing .venv

## Key decisions
- pyproject.toml uses dynamic version read from gsd_monitor/__init__.py via hatch
- No dev dependencies in pyproject.toml — kept minimal for installer use case
- start.bat template uses "%~dp0." (trailing dot) to resolve correctly from the installed dir
