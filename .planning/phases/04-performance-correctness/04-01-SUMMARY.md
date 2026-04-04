---
plan: 04-01
phase: 04-performance-correctness
status: complete
completed: 2026-04-04
key-files:
  modified:
    - gsd_monitor/api/app.py
    - gsd_monitor/services/project_discovery.py
    - frontend/src/pages/SettingsPage.tsx
    - frontend/src/context.tsx
---

## Summary

Three independent correctness patches applied to fix PERF-01, PERF-02, and PERF-04.

## What Was Built

**PERF-01 — Non-blocking FS watcher trylock** (`gsd_monitor/api/app.py`)
`_on_fs_change` now uses `acquire(blocking=False)`. If a scan is already running, the incoming FS event is silently dropped instead of queuing a redundant rescan that would overwrite in-flight results.

**PERF-02 — Scan directory exclusions** (`gsd_monitor/services/project_discovery.py`)
`_find_dirs` replaced `root.rglob()` with `os.walk(topdown=True)` + in-place `dirnames[:]` pruning. `_EXCLUDED_DIRS = {"node_modules", ".venv", ".git", "build", "dist"}` prevents descent into heavy directories, dramatically reducing discovery time on large repos.

**PERF-04 — Settings save race fix** (`frontend/src/pages/SettingsPage.tsx`, `frontend/src/context.tsx`)
Removed `await reload()` from `SettingsPage.save()` (and the now-unused `useApp`/`reload` imports). The WS handler in `context.tsx` now checks `data.type === "projects_updated"` before calling `reload()`, and explicitly ignores `settings_saved` events — preventing the double-reload stale-data flash.

## Decisions

- PERF-01: Chose trylock over event debounce to avoid the complexity of timer state
- PERF-02: `os.walk` with in-place pruning is the standard pattern for skipping subtrees
- PERF-04: Filter by event type at the WS handler level — simpler than coordinating reload timing in the component

## Self-Check: PASSED

All 16 tests pass. No regressions.
