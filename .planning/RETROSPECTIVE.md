# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v5.0 — Installation and Distribution

**Shipped:** 2026-07-18
**Phases:** 2 (17–18) | **Plans:** 3 | **Files:** 12 changed (+300/−45 lines)

### What Was Built
- `install.ps1`: single-script installer covering prereq checks (Git, Python 3.11+, Node.js, WebView2), clone, venv, pip install -e ., npm build, start.bat launcher, desktop shortcut — idempotent re-run detection via `.git` presence
- `upgrade.ps1` / `upgrade.bat`: standalone upgrade covering valid-install guard, git pull + pip install + npm ci + npm build, hash-based already-up-to-date detection
- `pyproject.toml` with hatchling dynamic version sourced from `gsd_monitor/__init__.py`
- `/api/version` endpoint + ShellLayout sidebar footer badge — version visible on every page

### What Worked
- **Audit-before-close discipline** — running the milestone audit before completion confirmed all 9 requirements were implemented despite unchecked REQUIREMENTS.md checkboxes; prevented a false "gap" from blocking the close
- **Small milestone scope** — 2 phases, 3 plans, single day — execution was fast and focused
- **pyproject.toml as version anchor** — using `dynamic = ["version"]` with hatch means the same `__version__` in `__init__.py` serves both pip and the API endpoint, zero duplication

### What Was Inefficient
- **REQUIREMENTS.md checkboxes never updated** — all 9 requirements shipped but the doc was never checked off during execution. Audit caught this as a documentation-only gap, but it required a special note in the archive and the root REQUIREMENTS-VERIFICATION.md workaround
- **Phase 18 has no planning directory** — executed inline without a phase folder, leaving a traceability gap (ROADMAP + commit are the only records)
- **Phase 17 missing VERIFICATION.md** — self-checks in SUMMARY confirmed delivery but no formal verification artifact was produced

### Patterns Established
- Milestone audit result as the verification record when formal VERIFICATION.md files are absent
- `pyproject.toml` dynamic version → `__init__.py` → `/api/version` → frontend as the canonical version chain
- Separate install vs upgrade scripts (rather than one script with flags) — reduces re-run risk and keeps upgrade path lighter

### Key Lessons
1. **Check off requirements during execution, not just at close** — a simple `[x]` update after each plan prevents documentation drift and removes ambiguity at milestone audit time
2. **Fast phases still need a phase directory** — even a single-plan phase like Phase 18 benefits from a minimal `18-xx-SUMMARY.md` for traceability; inline execution trades speed for auditability
3. **Root-level verification docs are useful for install-type requirements** — `REQUIREMENTS-VERIFICATION.md` at the project root is a better home for manual test steps than buried planning files

---

## Milestone: v3.0 — gsd-core Migration

**Shipped:** 2026-06-18
**Phases:** 2 | **Plans:** 4 | **Tasks:** 10

### What Was Built
- GsdCoreRoadmapParser for heading-based ROADMAP.md with emoji milestones, milestone-prefixed IDs, archived details blocks
- 8 new document types surfaced (REQUIREMENTS, VERIFICATION, SUMMARY, UI-SPEC, UI-REVIEW, HANDOFF, .continue-here, config.json)
- Complete GSD-2 (.gsd/) code removal from discovery, parsers, models, and tests
- StateParser progress extraction from 3 syntax variants with dashboard progress bars
- InsightsPage with Requirements traceability (gap highlighting), Waves visualization, and Archives browsing
- Resume context banner for .continue-here.md on dashboard

### What Worked
- **Two-phase structure** (Make it Work + Enhanced Visibility) cleanly separated backend parsing from frontend visualization
- **Wave-based parallelization** — backend Wave 1 completed before frontend Wave 2, avoiding integration conflicts
- **Static parser pattern** (GsdCoreRoadmapParser.parse) consistent with existing RoadmapParser kept code predictable
- **Boolean doc flags** (has_ui_spec, etc.) followed existing has_context/has_plan convention, minimizing design decisions
- **Milestone audit before close** caught DOCS-07 rendering gap and Waves tab error message — both fixed before shipping

### What Was Inefficient
- **DOCS-07 gap** — continue_here field was wired backend-to-API but never rendered in frontend. Caught only by milestone audit, not during phase execution
- **Phase 11 missing VERIFICATION.md** — formal verification never run despite UAT existing. Process gap carried as tech debt
- **Hardcoded hex literals** — 36 found in UI-REVIEW, partially fixed. Token extraction should have been part of Phase 12 plan

### Patterns Established
- config.json presence as authoritative gsd-core detection signal (ROADMAP heading sniff as fallback)
- Section-bounded requirement parsing (scan only active milestone section, ignore Validated/Future)
- Fetch-once display-from-cache pattern for tab-based pages (fetch on segment change, not tab switch)
- Per-item useState accordion pattern for collapsible sections

### Key Lessons
1. **Run milestone audit before closing** — caught a real functional gap (DOCS-07) that would have shipped broken
2. **Frontend rendering gaps hide behind "field exists" checks** — a boolean field reaching api.ts doesn't mean it's displayed. E2E flow verification matters.
3. **Section-bounded parsing prevents false matches** — RequirementsParser initially captured 35 items instead of 21 because it scanned the full file including Validated section

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 8 | 15 | Initial MVP — established parser, discovery, dashboard patterns |
| v2.0 | 2 | 4 | Feature pages — TDD drift computation, shared utils extraction |
| v3.0 | 2 | 4 | gsd-core migration — new parser, doc surfacing, GSD-2 removal, insights page |
| v4.0 | 3 | 10 | gsd-core full visibility — P0 correctness, P1 artifact parsing, P2 UI surface |
| v5.0 | 2 | 3 | Installation & distribution — install/upgrade scripts, version display |

### Cumulative Quality

| Milestone | Tests | Key Metric |
|-----------|-------|------------|
| v1.0 | ~28 | Discovery, parser, settings coverage |
| v2.0 | ~35 | Drift computation TDD |
| v3.0 | 82 | +25 parser tests, +11 state parser progress tests |
| v4.0 | 82+ | P0 regression tests for artifact fallback and collision |
| v5.0 | 82+ | No new tests (scripted install/upgrade not unit-testable) |

### Top Lessons (Verified Across Milestones)

1. Static parser pattern (ClassName.parse(path) -> ParseResult) scales cleanly across parser types
2. Wave-based plan execution (backend first, frontend second) prevents integration rework
3. Milestone audit catches gaps that per-phase verification misses — always run before close
4. Check off requirements during execution to prevent documentation drift at close time
