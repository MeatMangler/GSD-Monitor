---
phase: 11-gsd-core-support
plan: "01"
subsystem: backend
status: complete
tags:
  - parser
  - models
  - discovery
  - gsd-core
  - gsd2-removal
dependency_graph:
  requires:
    - "10-03-PLAN.md (existing discovery infrastructure)"
  provides:
    - "gsd_monitor/parsers/gsd_core_roadmap.py — GsdCoreRoadmapParser"
    - "gsd_monitor/models/enums.py — GsdVersion.CORE"
    - "gsd_monitor/models/core.py — extended PhaseEntry, GsdProject, StateInfo"
    - "gsd_monitor/services/project_discovery.py — gsd-core detection, enrichment, GSD-2 removal"
  affects:
    - "11-02-PLAN.md (frontend consumes new fields via JSON API)"
tech_stack:
  added:
    - "GsdCoreRoadmapParser — heading-based ROADMAP.md parser with emoji milestone markers, milestone-prefixed phase IDs, archived details blocks"
  patterns:
    - "Static parse(file_path) -> ParseResult pattern (consistent with RoadmapParser)"
    - "model_copy(update=...) for immutable GsdProject enrichment"
    - "try/except around all JSON parsing (T-11-01, T-11-02 threat mitigations)"
key_files:
  created:
    - "gsd_monitor/parsers/gsd_core_roadmap.py"
    - "tests/test_gsd_core_roadmap_parser.py"
    - "tests/test_state_parser_progress.py"
  modified:
    - "gsd_monitor/models/enums.py"
    - "gsd_monitor/models/core.py"
    - "gsd_monitor/parsers/state_parser.py"
    - "gsd_monitor/parsers/__init__.py"
    - "gsd_monitor/services/project_discovery.py"
    - "tests/test_roadmap_parser.py"
  deleted:
    - "gsd_monitor/parsers/gsd2_roadmap.py"
    - "tests/test_gsd2_stateparser.py"
decisions:
  - "Used config.json presence as primary gsd-core detection signal; ROADMAP.md heading sniff as fallback (D-02)"
  - "Milestone-prefixed IDs stored as PhaseEntry.code (e.g. '1-01'), numeric prefix in PhaseEntry.number (D-03)"
  - "Boolean flags for new doc types (has_ui_spec, has_ui_review, has_summary, has_requirements) consistent with existing has_context/has_plan pattern (D-05)"
  - "config.json summary extracts only 3 fields: workflow_mode, model_profile, branching_strategy (D-07)"
  - "StateParser progress extraction: YAML frontmatter first, then bold-inline, then pipe-table (D-09)"
metrics:
  duration: "7 minutes"
  completed: "2026-06-18"
  tasks: 3
  tests_added: 25
  tests_total: 53
  files_created: 3
  files_modified: 6
  files_deleted: 2
---

# Phase 11 Plan 01: Backend gsd-core Support Summary

**One-liner:** gsd-core detection and parsing via config.json+heading ROADMAP, new doc type flags, HANDOFF.json/config.json/progress surfacing, and full GSD-2 code removal — 53 tests pass.

## What Was Built

### Task 1: Models, GsdCoreRoadmapParser, StateParser Progress Extraction

**Models extended (gsd_monitor/models/enums.py, core.py):**
- `GsdVersion.CORE = "gsd-core"` added; `GsdVersion.V2` removed
- `PhaseEntry` gains: `has_ui_spec`, `has_ui_review`, `has_summary`, `has_requirements` (all `bool = False`)
- `GsdProject` gains: `handoff_info`, `continue_here`, `config_info`, `progress_percent`, `completed_phases`, `total_phases`
- `StateInfo` gains: `total_phases`, `completed_phases`, `progress_percent` (all `int = 0`)

**GsdCoreRoadmapParser (gsd_monitor/parsers/gsd_core_roadmap.py):**
- Parses heading-based ROADMAP.md with `## Phase N: Title` or `### Phase N: Title` syntax
- Extracts goals from `**Goal**: ...` lines within phase sections
- Determines phase status from `**Plans:** N/M plans complete` headers and `- [x]`/`- [ ]` checkboxes
- Parses milestone sections from `## vX.Y` headings with emoji status markers (✅ → COMPLETED, 🚀 → ACTIVE)
- Handles milestone-prefixed phase IDs: `Phase 1-01` → `code="1-01"`, `number=1`
- Handles archived milestones inside HTML `<details>/<summary>` blocks
- Returns `ParseResult.ok(GsdProject(..., version=GsdVersion.CORE))`

**StateParser enhanced (gsd_monitor/parsers/state_parser.py):**
- Extracts `total_phases`, `completed_phases`, `progress_percent` from three syntax variants:
  - YAML frontmatter `progress:` block (primary — used by gsd-core STATE.md)
  - Bold inline: `**total_phases:** 8` (colon-inside-bold format)
  - Pipe-table: `| total_phases | 8 |` (accepts `percent` as alias for `progress_percent`)

**Tests added:** 14 parser tests + 11 state parser progress tests = 25 new tests

### Task 2: Discovery Refactor — gsd-core Detection, Enrichment, GSD-2 Removal

**GSD-2 code removed from project_discovery.py:**
- Deleted `_discover_gsd2`, `_enrich_gsd2_project`, `_enrich_gsd2_slice` methods
- Removed `.gsd` directory scanning loop from `discover_groups`
- Removed `gsd2_repos` set and all GSD-2 deduplication logic

**gsd-core detection in `_build_gsd1_segment`:**
- Checks `base/config.json` first (authoritative signal per D-02, DETECT-01)
- Falls back to ROADMAP.md heading sniff (`## Phase N` pattern in first 2000 chars)
- Selects `GsdCoreRoadmapParser` vs `RoadmapParser` based on detection result

**New enrichment in `_enrich_phase`:**
- `has_ui_spec`: checks for `{padded}-UI-SPEC.md` in phase directory
- `has_ui_review`: checks for `{padded}-UI-REVIEW.md` in phase directory
- `has_summary`: non-empty `*-SUMMARY.md` glob in phase directory
- `has_requirements`: `planning_dir/REQUIREMENTS.md` exists (project-level)
- Preserves `code` field from parsed `PhaseEntry` (milestone-prefixed IDs)

**HANDOFF.json parsing (DOCS-06, T-11-01 mitigated):**
- Reads `base/HANDOFF.json` with `json.loads` wrapped in try/except
- Extracts `phase`, `plan`, `timestamp` keys with `.get()` defaults
- Stores as `{phase, plan, timestamp, paused: True}` in `project.handoff_info`

**.continue-here.md detection (DOCS-07):**
- Checks `base/.continue-here.md` existence → sets `project.continue_here = True`

**config.json surfacing (DOCS-08, T-11-02 mitigated):**
- Extracts 3-field summary dict with safe `.get()` defaults:
  - `workflow_mode` from `config["mode"]` or `config["workflow"]["discuss_mode"]`
  - `model_profile` from `config["model_profile"]`
  - `branching_strategy` from `config["git"]["branching_strategy"]`
- Stores in `project.config_info`

**Progress metrics (PROG-01, PROG-02):**
- After StateParser call, wires `si.total_phases`, `si.completed_phases`, `si.progress_percent` into `GsdProject` via `model_copy`

**parsers/__init__.py updated:** Replaced `Gsd2RoadmapParser/Gsd2Milestone/SliceEntry` exports with `GsdCoreRoadmapParser`

### Task 3: GSD-2 Test File Removal

- Deleted `tests/test_gsd2_stateparser.py` (3 tests for `_discover_gsd2` which no longer exists)
- Removed `test_gsd2_parse_roundtrip` from `tests/test_roadmap_parser.py` (imported deleted `Gsd2RoadmapParser`)
- Full test suite: 53 tests, 0 failures

## Commits

| Task | Hash | Description |
|------|------|-------------|
| 1 | 46e5a35 | feat(11-01): add GsdCoreRoadmapParser, model extensions, StateParser progress |
| 2 | 8cbbc96 | feat(11-01): discovery refactor — gsd-core detection, enrichment, GSD-2 removal |
| 3 | a99a57c | feat(11-01): remove GSD-2 test file and verify clean imports |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Bold inline regex matched wrong position for colon**
- **Found during:** Task 1 GREEN phase (test_bold_inline_progress failed)
- **Issue:** `**total_phases:** 10` has the colon inside the bold markers (`**total_phases:**`), not outside. Regex `\*\*total_phases\*\*:?` failed to match.
- **Fix:** Updated regex to `\*\*total_phases:?\*\*:?\s*(\d+)` to match both colon-inside and colon-outside variants
- **Files modified:** `gsd_monitor/parsers/state_parser.py`
- **Impact:** All 11 state parser progress tests now pass

**2. [Rule 3 - Blocking] parsers/__init__.py imported deleted Gsd2RoadmapParser**
- **Found during:** Task 2 test run
- **Issue:** `gsd_monitor/parsers/__init__.py` imported `Gsd2RoadmapParser, Gsd2Milestone, SliceEntry` from the deleted `gsd2_roadmap.py`, causing `ModuleNotFoundError` for all tests that import any parser
- **Fix:** Replaced GSD-2 exports with `GsdCoreRoadmapParser` in `__init__.py`
- **Files modified:** `gsd_monitor/parsers/__init__.py`

**3. [Rule 3 - Blocking] test_roadmap_parser.py imported Gsd2RoadmapParser**
- **Found during:** Task 2 test run
- **Issue:** `test_gsd2_parse_roundtrip` in `tests/test_roadmap_parser.py` imported `Gsd2RoadmapParser` inline — failed after deletion
- **Fix:** Removed the `test_gsd2_parse_roundtrip` test function (GSD-2 is no longer relevant)
- **Files modified:** `tests/test_roadmap_parser.py`

## Known Stubs

None — all new fields are populated from real filesystem data or default to zero/False/None when data is absent.

## Threat Flags

No new threat surface beyond what was documented in the plan's `<threat_model>`. Mitigations applied:
- T-11-01 (HANDOFF.json tampering): `json.loads` + try/except + `.get()` defaults
- T-11-02 (config.json tampering): `json.loads` + try/except + nested `.get()` defaults

## Self-Check: PASSED

- `gsd_monitor/parsers/gsd_core_roadmap.py` — FOUND
- `gsd_monitor/models/enums.py` (GsdVersion.CORE) — FOUND
- `gsd_monitor/models/core.py` (new fields) — FOUND
- `gsd_monitor/services/project_discovery.py` — FOUND
- `tests/test_gsd_core_roadmap_parser.py` — FOUND
- `tests/test_state_parser_progress.py` — FOUND
- `gsd_monitor/parsers/gsd2_roadmap.py` — CONFIRMED DELETED
- `tests/test_gsd2_stateparser.py` — CONFIRMED DELETED
- Commits 46e5a35, 8cbbc96, a99a57c — FOUND in git log
- Full test suite: 53/53 PASSED
