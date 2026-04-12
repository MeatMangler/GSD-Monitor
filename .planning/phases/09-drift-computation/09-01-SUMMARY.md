---
phase: 09-drift-computation
plan: 01
subsystem: api
tags: [drift, phase-status, project-discovery, tdd, pytest]

# Dependency graph
requires: []
provides:
  - "_compute_drift module-level helper in project_discovery.py"
  - "Real DriftIndicator values for all GSD-1 phases via _enrich_phase"
  - "Real DriftIndicator values for all GSD-2 slices via _enrich_gsd2_slice"
  - "GSD-2 last_updated fallback to plan_file.stat().st_mtime when no summary exists"
affects: [10-feature-pages, drift-page, dashboard-stats]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Injectable now param pattern: _compute_drift(..., now=None) defaults to datetime.now(tz=timezone.utc) for deterministic testing without freezegun"
    - "Module-level private helper before class definition for shared logic across methods"

key-files:
  created:
    - tests/test_drift_computation.py
  modified:
    - gsd_monitor/services/project_discovery.py

key-decisions:
  - "D-01: IN_PROGRESS with no plan returns DEFERRED — no plan means no meaningful work regardless of status"
  - "D-02: COMPLETE phase always returns NONE regardless of age — done is done"
  - "D-03: Shared _compute_drift helper called from both _enrich_phase and _enrich_gsd2_slice — no duplicated logic"
  - "D-04: Injectable now param for deterministic testing without external time-mocking libraries"
  - "D-05: GSD-2 _enrich_gsd2_slice falls back to plan_file.stat().st_mtime for last_updated when no summary exists — matches GSD-1 behavior"

patterns-established:
  - "TDD RED-GREEN: test file committed with ImportError (RED), then implementation committed to make all tests pass (GREEN)"
  - "Age boundary: >30 days = MAJOR, >=7 days = MINOR, <7 days = NONE (exactly 30 days is MINOR not MAJOR)"

requirements-completed: [DRFT-01]

# Metrics
duration: 2min
completed: 2026-04-12
---

# Phase 9 Plan 01: Drift Computation Summary

**_compute_drift helper computing NONE/MINOR/MAJOR/DEFERRED from plan age and phase status, replacing hardcoded DEFERRED in both GSD-1 and GSD-2 enrichment paths, with 13 TDD tests covering all edge cases and boundary conditions.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-12T12:18:42Z
- **Completed:** 2026-04-12T12:20:27Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Implemented `_compute_drift` module-level helper with injectable `now` param for deterministic testing
- Replaced hardcoded `DriftIndicator.DEFERRED` in `_enrich_phase` with live computed values
- Replaced hardcoded `DriftIndicator.DEFERRED` in `_enrich_gsd2_slice` with live computed values
- Added GSD-2 last_updated fallback to `plan_file.stat().st_mtime` (D-05) for consistent behavior across GSD versions
- 13 TDD tests pass covering all boundary conditions (30-day boundary, COMPLETE override, fallback chain)

## Task Commits

Each task was committed atomically:

1. **Task 1: RED — Write failing tests for _compute_drift** - `24b0b8d` (test)
2. **Task 2: GREEN — Implement _compute_drift and wire into enrichment** - `d242ad0` (feat)

_Note: TDD tasks have two commits: test (RED) then feat (GREEN)._

## Files Created/Modified

- `tests/test_drift_computation.py` — 13 unit tests for all drift computation rules, boundaries, and edge cases
- `gsd_monitor/services/project_discovery.py` — `_compute_drift` helper added; both `_enrich_phase` and `_enrich_gsd2_slice` wired to call it; GSD-2 `last_updated` fallback added

## Decisions Made

- Injectable `now` param over freezegun: avoids external test dependency, matches existing codebase style
- Age boundary uses `> 30` for MAJOR (not `>= 30`), so exactly 30 days is MINOR — consistent with "grace period" intent
- COMPLETE status short-circuits before age check — prevents completed phases from ever showing drift

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 10 (Feature Pages) can now consume real `drift` values from the API
- `DriftPage` table sorting (MAJOR first) will work correctly because string enum values match frontend `p.drift === "major"` checks
- Dashboard drift stat card counts are now accurate

---
*Phase: 09-drift-computation*
*Completed: 2026-04-12*
