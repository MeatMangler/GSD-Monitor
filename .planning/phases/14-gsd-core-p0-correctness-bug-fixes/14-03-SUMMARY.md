---
phase: 14-gsd-core-p0-correctness-bug-fixes
plan: "03"
subsystem: parsers, services, models, tests
tags: [discovery, plan-parser, requirements-parser, reserved-dirs, xml-tasks]
status: complete
requirements: [VIS-P0-03, VIS-P0-04]
depends_on: [14-01, 14-02]
key-files:
  modified:
    - gsd_monitor/parsers/plan_parser.py
    - gsd_monitor/parsers/__init__.py
    - gsd_monitor/services/planning_layout.py
    - gsd_monitor/services/project_discovery.py
    - gsd_monitor/models/core.py
    - tests/test_discovery_gsd_core.py
decisions:
  - "Added has_requirements to GsdProject (not just PhaseEntry) so discovery pipeline can surface project-level requirements flag alongside the parsed list"
metrics:
  completed: "2026-07-18"
  tasks_completed: 8
  tests_before: 89
  tests_after: 95
---

# Phase 14 Plan 03: XML Task Parsing, RequirementsParser Wiring, Reserved Dir Hardening Summary

Three bundled fixes for VIS-P0-03 and VIS-P0-04: XML `<task>` block extraction in PlanParser, RequirementsParser wired into the discovery pipeline and exported from the parsers package, and six new reserved directory names added to prevent gsd-core artifact dirs from being walked as sub-projects.

## What Was Implemented

### Task 1: XML Task Parsing in PlanParser

Added `_XML_TASK` regex pattern to `gsd_monitor/parsers/plan_parser.py` matching `<task id="..." status="...">text</task>` blocks (gsd-core XML format). The `PlanParser.parse()` method now runs both the existing `_TASK_LINE` markdown checkbox extractor and the new `_XML_TASK` extractor on the same text, so files with both formats produce combined todos. Status values `done`, `complete`, `completed`, and `x` map to `is_checked=True`.

### Task 2: Export RequirementsParser from parsers/__init__.py

Added `from gsd_monitor.parsers.requirements_parser import RequirementsParser, RequirementEntry` to `gsd_monitor/parsers/__init__.py` and added both names to `__all__`. The parser was already implemented but not exported from the package, making it hard to use from outside.

### Task 3: Reserved Dir Hardening

Added `spikes`, `sketches`, `reports`, `todos`, `debug`, `intel` to the `RESERVED` frozenset in `gsd_monitor/services/planning_layout.py`. These are standard gsd-core artifact directories that contain content files, not sub-projects. Without them in RESERVED, `iter_planning_contexts` would walk them and produce spurious sub-segments.

### Task 4: Wire RequirementsParser into Discovery

In `gsd_monitor/services/project_discovery.py`:
- Added `from gsd_monitor.parsers.requirements_parser import RequirementsParser` import
- In `_build_gsd1_segment`, after the config_info block, added a REQUIREMENTS.md check that calls `RequirementsParser.parse(str(base))` and updates the project with `has_requirements=True` and the parsed `requirements` list

### Task 5/6: GsdProject Model Fields

Added two fields to `GsdProject` in `gsd_monitor/models/core.py`:
- `has_requirements: bool = Field(default=False)` — project-level flag (previously only existed on `PhaseEntry`)
- `requirements: list[Any] = Field(default_factory=list)` — parsed `RequirementEntry` objects (using `Any` to avoid circular import from parsers layer)

### Task 7 (Tests): 6 New Tests in 3 Classes

Added to `tests/test_discovery_gsd_core.py`:
- `TestXmlTaskParsing` (2 tests): verifies `<task>` XML blocks produce todos, and that mixed markdown+XML files produce all todos combined
- `TestReservedDirHardening` (2 tests): verifies all 6 new names are in RESERVED, and that a `spikes/ROADMAP.md` does not produce a spurious sub-segment
- `TestRequirementsParserExport` (2 tests): verifies RequirementsParser is importable from the package, and that a project with REQUIREMENTS.md gets `has_requirements=True` and a non-empty `requirements` list with correct IDs

## Test Results

```
95 passed in 1.46s
```

- Before: 89 passing
- After: 95 passing (+6 new tests, 0 regressions)

## Files Changed

| File | Change |
|------|--------|
| `gsd_monitor/parsers/plan_parser.py` | Added `_XML_TASK` pattern + extraction loop in `parse()` |
| `gsd_monitor/parsers/__init__.py` | Export `RequirementsParser`, `RequirementEntry` |
| `gsd_monitor/services/planning_layout.py` | Added 6 dirs to `RESERVED` frozenset |
| `gsd_monitor/services/project_discovery.py` | Import + call `RequirementsParser` in `_build_gsd1_segment` |
| `gsd_monitor/models/core.py` | Added `has_requirements`, `requirements` fields to `GsdProject` |
| `tests/test_discovery_gsd_core.py` | Added 3 test classes with 6 tests |

## Deviations from Plan

### Auto-added: has_requirements field on GsdProject

**Rule 2 (missing critical functionality):** The plan's test `test_requirements_surfaced_on_project` asserts `proj.has_requirements is True` where `proj` is a `GsdProject`. But `has_requirements` only existed on `PhaseEntry`. Added it to `GsdProject` and wired it in `_build_gsd1_segment` to correctly surface the project-level requirements presence flag.

- **Found during:** Task 6 (writing tests)
- **Fix:** Added `has_requirements: bool = False` to `GsdProject` and included it in the `model_copy` call in the requirements block
- **Files modified:** `gsd_monitor/models/core.py`, `gsd_monitor/services/project_discovery.py`
- **Commit:** ae6cc7d

## Self-Check: PASSED

- `gsd_monitor/parsers/plan_parser.py` — exists, contains `_XML_TASK`
- `gsd_monitor/parsers/__init__.py` — exists, exports `RequirementsParser`
- `gsd_monitor/services/planning_layout.py` — exists, contains `spikes` in RESERVED
- `gsd_monitor/services/project_discovery.py` — exists, calls `RequirementsParser.parse`
- `gsd_monitor/models/core.py` — exists, has `requirements` and `has_requirements` on `GsdProject`
- `tests/test_discovery_gsd_core.py` — exists, contains 3 new test classes
- Commit ae6cc7d verified in git log
- 95 tests passing, 0 failures
