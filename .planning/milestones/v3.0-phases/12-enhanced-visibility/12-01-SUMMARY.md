---
phase: 12-enhanced-visibility
plan: 01
subsystem: backend
tags: [requirements-parser, insights-api, milestone-model, wave-data]
requires: []
provides: [RequirementsParser, insights-endpoint, Milestone.is_archived]
affects: [gsd_monitor/api/app.py, gsd_monitor/models/core.py, gsd_monitor/parsers/]
tech_stack:
  added: []
  patterns: [static-parser-method, regex-frontmatter-parse, pydantic-basemodel]
key_files:
  created:
    - gsd_monitor/parsers/requirements_parser.py
  modified:
    - gsd_monitor/models/core.py
    - gsd_monitor/parsers/gsd_core_roadmap.py
    - gsd_monitor/api/app.py
decisions:
  - Bound REQUIREMENTS.md parsing to v3.0 section only (stops at next ## heading) to exclude v2.0 Validated and Future Requirements items — ensures exactly 21 v3.0 requirements
  - Used regex-only frontmatter parsing in _extract_wave_data (no yaml import) consistent with existing codebase pattern
  - Placed insights endpoint after quick-tasks and before docs-tree following plan placement instruction
metrics:
  duration: "3m 22s"
  completed: "2026-06-18"
  tasks_completed: 2
  files_changed: 4
status: complete
---

# Phase 12 Plan 01: Backend Data Layer for Enhanced Visibility — Summary

**One-liner:** Requirements traceability parser, wave extraction helper, and /api/insights endpoint providing the data layer for all four VIS requirements.

## What Was Built

### Task 1: RequirementsParser and Milestone Model Updates

**`gsd_monitor/parsers/requirements_parser.py`** — new file

- `RequirementEntry` Pydantic model with fields: `id`, `category`, `description`, `is_checked`, `phase`, `status`, `is_gap`
- `RequirementsParser.parse(planning_dir)` static method — three-pass regex approach:
  1. `_TRACE_SECTION` / `_TRACE_ROW` — builds traceability map from `## Traceability` table
  2. `_V3_SECTION` / `_SECTION_HDR` — bounds requirement scanning to `## v3.0 Requirements` only
  3. `_CATEGORY_HDR` / `_REQ_LINE` — extracts requirements with category and checkbox state
- Gap detection: `is_gap=True` when no traceability row exists for a requirement ID

**`gsd_monitor/models/core.py`** — `Milestone` class extended

- Added `is_archived: bool = False`
- Added `completion_date: str | None = None`

**`gsd_monitor/parsers/gsd_core_roadmap.py`** — archived milestone enrichment

- Added `_SHIPPED_DATE = re.compile(r"SHIPPED\s+(\d{4}-\d{2}-\d{2})")` at module level
- `_extract_archived_milestones` now sets `is_archived=True` and extracts `completion_date` from `<summary>` text
- `_parse_milestones` renumbering loop now preserves `is_archived` and `completion_date` fields

### Task 2: Insights API Endpoint

**`gsd_monitor/api/app.py`** — new endpoint and helper

- `_extract_wave_data(planning_dir)` helper function (module-level, outside create_app):
  - Iterates all subdirectories under `.planning/phases/`
  - Reads each `*-PLAN.md` file and extracts `wave:` from YAML frontmatter using regex
  - Filters to phases where plans span more than one distinct wave value
  - Returns sorted list of `{phase_number, phase_title, plans}` dicts
- `GET /api/insights/{planning_path:path}` endpoint:
  - URL-decodes `planning_path`
  - Calls `RequirementsParser.parse()` and `_extract_wave_data()`
  - Returns `{"requirements": [...], "wave_phases": [...]}`
- Added `from gsd_monitor.parsers.requirements_parser import RequirementsParser` import

## Verification Results

All plan-level verifications passed:

```
OK: 21 requirements
OK: 7 wave phases (phases 1, 3, 4, 7, 10, 11, 12 have multi-wave plans)
OK: Milestone.is_archived works
OK: _extract_wave_data returns phase 11 (multi-wave) and excludes phase 9 (single-wave)
```

Task 1 acceptance criteria:
- 21 requirements parsed from `.planning/REQUIREMENTS.md` (v3.0 section only)
- All requirements have non-empty category matching their `###` section heading
- VIS-01..VIS-04 have `phase="Phase 12"` and `status="Pending"`
- DETECT-01 has `is_checked=True`, `phase="Phase 11"`, `status="Complete"`
- `Milestone.is_archived` and `Milestone.completion_date` fields present with correct defaults
- `_extract_archived_milestones` sets `is_archived=True` and extracts `completion_date` from SHIPPED dates

Task 2 acceptance criteria:
- Endpoint registered at `/api/insights/{planning_path:path}`
- Phase 11 appears in wave_phases (wave 1 and wave 2 plans)
- Phase 9 filtered out (single-plan, single-wave)
- Response shape: `{"requirements": [...], "wave_phases": [...]}`

## Commits

- `07892d5` feat(12-01): add RequirementsParser and extend Milestone model
- `ad104a8` feat(12-01): add GET /api/insights endpoint with wave data extraction

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] REQUIREMENTS.md parser was capturing 14 extra "Validated" requirements**

- **Found during:** Task 1 verification (35 parsed instead of expected 21)
- **Issue:** The `_REQ_LINE` regex matched `- [x] **DRFT-01**: description` lines in the `## Validated (v2.0 — shipped)` section, which uses the identical format. The plan's action did not specify bounding the scan region.
- **Fix:** Added `_V3_SECTION` and `_SECTION_HDR` regexes. `parse()` now extracts only the text between `## v3.0 Requirements` and the next `##` heading, then runs `_REQ_LINE` within that bounded region only.
- **Files modified:** `gsd_monitor/parsers/requirements_parser.py`
- **Commit:** `07892d5`

## Known Stubs

None — all data flows are wired. The endpoint returns real data from parsed files.

## Threat Flags

T-12-01 (planning_path untrusted input) mitigation applied: `unquote(planning_path)` called before passing to parsers. The parsers themselves use `Path(planning_dir) / "REQUIREMENTS.md"` and `Path(planning_dir) / "phases"` — only reading inside the given directory, consistent with existing quick-tasks and docs endpoints.
