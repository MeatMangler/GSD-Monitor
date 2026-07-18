---
phase: 14-gsd-core-p0-correctness-bug-fixes
plan: "01"
subsystem: discovery
tags: [bug-fix, gsd-core, artifact-resolution]
dependency_graph:
  requires: []
  provides: [_resolve_artifact helper, bare-artifact fallback for gsd-core phases]
  affects: [gsd_monitor/services/project_discovery.py]
tech_stack:
  added: []
  patterns: [prefixed-then-bare artifact resolution]
key_files:
  created: []
  modified:
    - gsd_monitor/services/project_discovery.py
    - tests/test_discovery_gsd_core.py
decisions:
  - "Module-level helper _resolve_artifact placed after _try_read_json, before _compute_drift per plan spec"
  - "Caller still checks .is_file() — helper only resolves path, no existence guarantee"
metrics:
  duration: "~5 minutes"
  completed: "2026-07-18"
status: complete
---

# Phase 14 Plan 01: Unprefixed Artifact Fallback Summary

One-liner: Added `_resolve_artifact` helper that tries `{padded}-NAME.md` first then falls back to bare `NAME.md` for all 6 artifact types in `_enrich_phase`.

## What Was Implemented

**Bug fixed (VIS-P0-01):** gsd-core phase directories store artifact files without numeric prefixes (e.g., `CONTEXT.md` instead of `03-CONTEXT.md`). The previous implementation only checked for the prefixed form, leaving `has_context`, `has_research`, `has_uat`, and `has_validation` always `False` for gsd-core phases.

**Solution:** Added `_resolve_artifact(phase_dir, padded, name)` as a module-level helper function in `gsd_monitor/services/project_discovery.py`. The function:
1. Constructs the prefixed path (`{padded}-{name}`) and checks `is_file()`
2. Returns the prefixed path if it exists (backward compatible with GSD-1)
3. Falls back to the bare path (`{name}`) otherwise
4. The caller retains all `is_file()` checks — the helper only resolves the path

Wired into `_enrich_phase` for all 6 artifact lookups: `VALIDATION.md`, `VERIFICATION.md`, `CONTEXT.md`, `RESEARCH.md`, `UAT.md`, `UI-SPEC.md`, `UI-REVIEW.md`.

## Test Results

Full suite: **87 passed, 0 failed** (1.67s)

New `TestUnprefixedArtifactFallback` class: **5/5 passed**
- `test_bare_context_found` — bare `CONTEXT.md` sets `has_context=True`
- `test_bare_research_found` — bare `RESEARCH.md` sets `has_research=True` and populates `research_content`
- `test_bare_verification_found` — bare `VERIFICATION.md` sets `has_validation=True` and populates `validation_content`
- `test_bare_uat_found` — bare `UAT.md` sets `has_uat=True`
- `test_prefixed_takes_precedence_over_bare` — prefixed form wins when both exist

## Files Changed

| File | Change |
|------|--------|
| `gsd_monitor/services/project_discovery.py` | Added `_resolve_artifact` helper (17 lines); replaced 7 hard-coded `phase_dir / f"{padded}-{name}"` constructions in `_enrich_phase` |
| `tests/test_discovery_gsd_core.py` | Added `TestUnprefixedArtifactFallback` class with 5 tests |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `gsd_monitor/services/project_discovery.py` — exists, contains `_resolve_artifact`
- `tests/test_discovery_gsd_core.py` — exists, contains `TestUnprefixedArtifactFallback`
- Commit `437874c` — exists in git log
- 87/87 tests pass
