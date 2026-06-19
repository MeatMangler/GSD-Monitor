---
phase: 11
slug: gsd-core-support
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-18
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml |
| **Quick run command** | `python -m pytest tests/test_discovery_gsd_core.py tests/test_gsd_core_roadmap_parser.py tests/test_state_parser_progress.py -x -v` |
| **Full suite command** | `python -m pytest tests/ -x -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_discovery_gsd_core.py tests/test_gsd_core_roadmap_parser.py tests/test_state_parser_progress.py -x -v`
- **After every plan wave:** Run `python -m pytest tests/ -x -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | DETECT-01 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestGsdCoreDetection -v` | Yes | green |
| 11-01-01 | 01 | 1 | DETECT-02 | — | N/A | unit | `pytest tests/test_gsd_core_roadmap_parser.py::test_parse_heading_phases -v` | Yes | green |
| 11-01-01 | 01 | 1 | DETECT-03 | — | N/A | unit | `pytest tests/test_gsd_core_roadmap_parser.py::test_milestone_emoji_completed tests/test_gsd_core_roadmap_parser.py::test_milestone_emoji_active -v` | Yes | green |
| 11-01-01 | 01 | 1 | DETECT-04 | — | N/A | unit | `pytest tests/test_gsd_core_roadmap_parser.py::test_milestone_prefixed_phase_ids -v` | Yes | green |
| 11-01-01 | 01 | 1 | DETECT-05 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestGsdCoreDetection::test_checkbox_roadmap_stays_gsd1 tests/test_roadmap_parser.py::test_parse_checkbox_phases -v` | Yes | green |
| 11-01-01 | 01 | 1 | DETECT-06 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestGsd2Removal -v` | Yes | green |
| 11-01-01 | 01 | 1 | DOCS-01 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestDocTypeFlags::test_has_requirements -v` | Yes | green |
| 11-01-01 | 01 | 1 | DOCS-02 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestDocTypeFlags -v` | Yes | green |
| 11-01-01 | 01 | 1 | DOCS-03 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestDocTypeFlags::test_has_summary -v` | Yes | green |
| 11-01-01 | 01 | 1 | DOCS-04 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestDocTypeFlags::test_has_ui_spec -v` | Yes | green |
| 11-01-01 | 01 | 1 | DOCS-05 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestDocTypeFlags::test_has_ui_review -v` | Yes | green |
| 11-01-02 | 01 | 1 | DOCS-06 | T-11-01 | json.loads + try/except + .get() defaults | unit | `pytest tests/test_discovery_gsd_core.py::TestHandoffJson -v` | Yes | green |
| 11-01-02 | 01 | 1 | DOCS-07 | — | N/A | unit | `pytest tests/test_discovery_gsd_core.py::TestContinueHere -v` | Yes | green |
| 11-01-02 | 01 | 1 | DOCS-08 | T-11-02 | json.loads + try/except + nested .get() defaults | unit | `pytest tests/test_discovery_gsd_core.py::TestConfigInfoSurfacing -v` | Yes | green |
| 11-01-01 | 01 | 1 | PROG-01 | — | N/A | unit | `pytest tests/test_state_parser_progress.py -v` | Yes | green |
| 11-02-01 | 02 | 2 | PROG-02 | — | N/A | build+UAT | `cd frontend && npx tsc -b --noEmit && npm run build` | Yes | green |
| 11-01-01 | 01 | 1 | PROG-03 | — | N/A | unit | `pytest tests/test_state_parser_progress.py::test_yaml_frontmatter_progress tests/test_state_parser_progress.py::test_bold_inline_progress tests/test_state_parser_progress.py::test_pipe_table_progress -v` | Yes | green |

*Status: pending · green · red · flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Progress bar renders correctly in UI | PROG-02 | Frontend visual element; TypeScript build verifies compilation only | Start app, verify 4px compact and 8px detail progress bars render with correct fill |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 2s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-18

---

## Validation Audit 2026-06-18

| Metric | Count |
|--------|-------|
| Gaps found | 1 |
| Resolved | 1 |
| Escalated | 0 |
