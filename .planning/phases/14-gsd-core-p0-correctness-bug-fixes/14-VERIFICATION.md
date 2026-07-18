---
phase: 14-gsd-core-p0-correctness-bug-fixes
verified: 2026-07-18T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 14: GSD-Core P0 Correctness Bug Fixes — Verification Report

**Phase Goal:** Fix five P0 correctness bugs in the gsd-core discovery pipeline: unprefixed artifact resolution, milestone-phase directory collision, XML task extraction, reserved-dir hardening, and RequirementsParser wiring.
**Verified:** 2026-07-18
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Bare `CONTEXT.md`, `RESEARCH.md`, `VERIFICATION.md`, `UAT.md` set the corresponding `has_*` flags to `true` and populate content fields | VERIFIED | `_resolve_artifact` (project_discovery.py:68-83) tries prefixed then falls back to bare; `has_validation = validation_file.is_file() or verification_file.is_file()` (line 569); `TestUnprefixedArtifactFallback` — 5/5 tests pass |
| 2 | Phases `1-01`, `1-02`, `1-03` each enrich from their own `01-01-*`, `01-02-*`, `01-03-*` directories with no collision | VERIFIED | `_phase_dir_prefix` (project_discovery.py:86-105) zero-pads each segment of the dash-separated code; `TestPhaseEnrichmentCollision::test_each_phase_enriches_own_directory` asserts distinct todo counts (1, 2, 3) per phase — PASSES |
| 3 | A gsd-core `XX-YY-PLAN.md` with `<task>` XML blocks produces a non-empty `todos` list | VERIFIED | `_XML_TASK` regex (plan_parser.py:23-26) with `DOTALL` matches single- and multi-line task blocks; `PlanParser.parse()` runs both checkbox and XML extractors; `TestXmlTaskParsing` — 2/2 tests pass |
| 4 | Directories `spikes`, `sketches`, `reports`, `todos`, `debug`, `intel` are in `RESERVED` and not walked as fake projects | VERIFIED | `RESERVED` frozenset in planning_layout.py:9-28 contains all 6 names; `TestReservedDirHardening::test_spikes_not_walked_as_project` asserts all 6 present; `test_spikes_dir_not_surfaced_as_segment` confirms no spurious segment — PASSES |
| 5 | `RequirementsParser` is called from the discovery pipeline; requirements appear in API responses for projects with `REQUIREMENTS.md` | VERIFIED | `from gsd_monitor.parsers.requirements_parser import RequirementsParser` import at project_discovery.py:27; called in `_build_gsd1_segment` (lines 422-426); `RequirementsParser` and `RequirementEntry` exported in `parsers/__init__.py`; `TestRequirementsParserExport::test_requirements_surfaced_on_project` asserts `proj.has_requirements is True`, `len(proj.requirements) > 0`, and correct IDs — PASSES |

**Score:** 5/5 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `gsd_monitor/services/project_discovery.py` | `_resolve_artifact` and `_phase_dir_prefix` helpers; `RequirementsParser` import and call in `_build_gsd1_segment` | VERIFIED | Lines 68-105 (helpers), line 27 (import), lines 422-426 (call) — all present and substantive |
| `gsd_monitor/parsers/plan_parser.py` | `_XML_TASK` regex; XML extraction loop in `PlanParser.parse()` | VERIFIED | Lines 23-26 (regex), lines 46-51 (extraction loop) — present and wired |
| `gsd_monitor/parsers/__init__.py` | `RequirementsParser` and `RequirementEntry` exported in `__all__` | VERIFIED | Lines 3 and 13-14 — both exported |
| `gsd_monitor/services/planning_layout.py` | `RESERVED` frozenset contains 6 new dirs | VERIFIED | Lines 21-27 — all 6 present: `spikes`, `sketches`, `reports`, `todos`, `debug`, `intel` |
| `gsd_monitor/models/core.py` | `GsdProject` has `has_requirements: bool` and `requirements: list[Any]` fields | VERIFIED | Lines 81-82 — both fields present with correct defaults |
| `tests/test_discovery_gsd_core.py` | `TestUnprefixedArtifactFallback` (5 tests), `TestPhaseEnrichmentCollision` (2 tests), `TestXmlTaskParsing` (2 tests), `TestReservedDirHardening` (2 tests), `TestRequirementsParserExport` (2 tests) | VERIFIED | All 13 new tests present and passing |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `_enrich_phase` | `_resolve_artifact` | Called for all 7 artifact lookups (VALIDATION, VERIFICATION, CONTEXT, RESEARCH, UAT, UI-SPEC, UI-REVIEW) | WIRED | Lines 552-563: every artifact resolved through `_resolve_artifact` |
| `_enrich_phase` | `_phase_dir_prefix` | `padded = _phase_dir_prefix(phase)` on line 503 | WIRED | Single call replaces the old hardcoded `f"{phase.number:02d}"` |
| `_build_gsd1_segment` | `RequirementsParser.parse()` | `req_path.is_file()` guard → `RequirementsParser.parse(str(base))` | WIRED | Lines 422-426 — guard + call + model_copy update |
| `PlanParser.parse()` | `_XML_TASK` regex | `_XML_TASK.finditer(text)` in main parse loop | WIRED | Lines 46-51 — result appended to same `todos` list as markdown tasks |
| `iter_planning_contexts` | `RESERVED` | `if d.name in RESERVED` guard on line 84 | WIRED | Existing guard now covers 6 additional names |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `TestUnprefixedArtifactFallback` (SC-1) | `python -m pytest tests/test_discovery_gsd_core.py::TestUnprefixedArtifactFallback -v` | 5 passed | PASS |
| `TestPhaseEnrichmentCollision` (SC-2) | `python -m pytest tests/test_discovery_gsd_core.py::TestPhaseEnrichmentCollision -v` | 2 passed | PASS |
| `TestXmlTaskParsing` (SC-3) | `python -m pytest tests/test_discovery_gsd_core.py::TestXmlTaskParsing -v` | 2 passed | PASS |
| `TestReservedDirHardening` (SC-4) | `python -m pytest tests/test_discovery_gsd_core.py::TestReservedDirHardening -v` | 2 passed | PASS |
| `TestRequirementsParserExport` (SC-5) | `python -m pytest tests/test_discovery_gsd_core.py::TestRequirementsParserExport -v` | 2 passed | PASS |
| Full test suite | `python -m pytest tests/ -v` | **95 passed in 1.33s** | PASS |

---

## Git Commit Verification

| Commit | Message | Scope |
|--------|---------|-------|
| `437874c` | `fix(discovery): unprefixed artifact fallback for gsd-core phase dirs (VIS-P0-01)` | SC-1 |
| `5b87c00` | `fix(discovery): phase-dir enrichment collision for milestone-prefixed phases (VIS-P0-02)` | SC-2 |
| `ae6cc7d` | `fix(discovery): XML task parsing, RequirementsParser wiring, reserved dir hardening (VIS-P0-03, VIS-P0-04)` | SC-3, SC-4, SC-5 |

All three commits confirmed present in `git log`.

---

## Anti-Patterns Found

No anti-patterns found. No TBD/FIXME/XXX markers, no stub returns, no hardcoded empty arrays in implementation paths.

---

## Human Verification Required

None. All success criteria are mechanically verifiable and fully exercised by the test suite.

---

## Gaps Summary

No gaps. All five success criteria are met by substantive, wired implementations backed by 13 passing targeted tests and a clean 95/95 full suite run.

---

_Verified: 2026-07-18T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
