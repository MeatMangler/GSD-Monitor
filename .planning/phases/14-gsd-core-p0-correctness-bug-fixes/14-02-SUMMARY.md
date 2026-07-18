---
phase: 14-gsd-core-p0-correctness-bug-fixes
plan: "02"
subsystem: discovery
tags: [bug-fix, phase-enrichment, milestone-phases, p0]
requirements: [VIS-P0-02]
key-files:
  modified:
    - gsd_monitor/services/project_discovery.py
    - tests/test_discovery_gsd_core.py
decisions:
  - "_phase_dir_prefix zero-pads each part of a milestone phase code so 1-01 → 01-01, 1-02 → 01-02, giving each sub-phase a unique directory prefix"
metrics:
  duration: "< 5 minutes"
  completed: "2026-07-18"
  tasks_completed: 5
  tasks_total: 5
  tests_added: 2
  tests_passed: 89
status: complete
---

# Phase 14 Plan 02: Phase-Dir Enrichment Collision Fix Summary

**One-liner:** Added `_phase_dir_prefix` helper that zero-pads each segment of a milestone phase code so phases 1-01, 1-02, 1-03 each match their own directory (01-01-*, 01-02-*, 01-03-*) instead of all colliding on the common "01-" prefix.

## What Was Implemented

### Root Cause (VIS-P0-02)

`_enrich_phase` computed `padded = f"{phase.number:02d}"` for all phases. For milestone-prefixed phases like 1-01, 1-02, 1-03, all three have `number=1`, so `padded` was always `"01"`. The directory `startswith("01-")` check matched all three directories (`01-01-alpha`, `01-02-beta`, `01-03-gamma`) and returned the first hit for every phase — causing all three sub-phases to read plan content from `01-01-alpha`.

### Fix

Added module-level helper `_phase_dir_prefix(phase: "PhaseEntry") -> str` (placed between `_resolve_artifact` and `_compute_drift`) that:

- For plain phases (no code): returns `f"{phase.number:02d}"` — unchanged behavior.
- For milestone-prefixed phases (code contains `-`): splits the code on `-`, zero-pads each numeric part to 2 digits, and rejoins with `-`. Example: `code="1-01"` → `"01-01"`.

`_enrich_phase` now uses `padded = _phase_dir_prefix(phase)` instead of the hardcoded format string. The `_find_archive_phase_dir` call already received `padded` as a parameter, so it automatically benefits from the fix.

### Tests Added (`TestPhaseEnrichmentCollision`)

Two regression tests added to `tests/test_discovery_gsd_core.py`:

1. **`test_each_phase_enriches_own_directory`** — Creates a repo with three milestone sub-phase directories (`01-01-alpha`, `01-02-beta`, `01-03-gamma`), each containing a plan file with a distinct number of todo items (1, 2, 3). Asserts that after discovery, phases 1-01, 1-02, and 1-03 each report the correct todo count, proving no collision occurred.

2. **`test_plain_phase_unaffected`** — Creates a repo with a plain phase (number=3, no code) in directory `03-doc-browser`. Asserts that the plain-phase path continues to work correctly, confirming the fix is non-breaking.

## Test Results

```
tests/test_discovery_gsd_core.py::TestPhaseEnrichmentCollision::test_each_phase_enriches_own_directory PASSED
tests/test_discovery_gsd_core.py::TestPhaseEnrichmentCollision::test_plain_phase_unaffected PASSED

89 passed in 1.27s
```

All 89 tests in the suite pass. No regressions.

## Files Changed

| File | Change |
|------|--------|
| `gsd_monitor/services/project_discovery.py` | Added `_phase_dir_prefix` helper (21 lines); updated `_enrich_phase` to call it (1 line change) |
| `tests/test_discovery_gsd_core.py` | Added `TestPhaseEnrichmentCollision` class with 2 tests (134 lines) |

## Commit

`5b87c00` — `fix(discovery): phase-dir enrichment collision for milestone-prefixed phases (VIS-P0-02)`

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `gsd_monitor/services/project_discovery.py` — exists, contains `_phase_dir_prefix`
- `tests/test_discovery_gsd_core.py` — exists, contains `TestPhaseEnrichmentCollision`
- Commit `5b87c00` — verified in git log
- 89 tests pass, 0 failures
