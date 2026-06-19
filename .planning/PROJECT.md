# GSD Monitor

## What This Is

GSD Monitor is a Windows desktop companion app (Python + pywebview + React) that discovers GSD projects on disk and gives developers an immediate visual overview of every GSD workflow document. It scans configured directories, classifies GSD-1 (`.planning/`) and gsd-core projects, and surfaces roadmap phases, planning docs, progress metrics, requirements traceability, and project status through a local FastAPI + React UI rendered in Edge WebView2.

## Core Value

A developer opens GSD Monitor and within seconds understands exactly where every project stands — which phases are done, what's active, and can read any planning doc — with zero duplicate entries and zero confusion about which project they're looking at.

## Current State (v3.0 — Shipped 2026-06-18)

All 21 v3.0 requirements delivered across 2 phases (12 phases total across 3 milestones):

- **gsd-core support**: Detects gsd-core projects via config.json, parses heading-based ROADMAP.md with milestone-prefixed phase IDs, emoji milestone markers, and archived details blocks
- **Document surfacing**: 8 new doc types — REQUIREMENTS, VERIFICATION, SUMMARY, UI-SPEC, UI-REVIEW, HANDOFF.json, .continue-here.md, config.json
- **Progress metrics**: StateParser extracts progress from 3 syntax variants; dashboard shows compact and detail progress bars
- **Pause/resume**: HANDOFF.json pause banner and .continue-here.md resume context banner on dashboard
- **InsightsPage**: Three-tab page with requirements traceability (gap highlighting), wave visualization, and milestone archive browsing
- **GSD-2 removed**: Complete removal of `.gsd/` code path from discovery, parsers, models, and tests

**Codebase:** 4,626 LOC (Python + TypeScript), 82 tests passing

### Requirements

#### Validated

- ✓ All 16 v1.0 requirements — v1.0 (worktree dedup, dashboard, doc browser, performance, StateParser, FastAPI modernization)
- ✓ All 14 v2.0 requirements — v2.0 (drift computation, drift/quick tasks/verification pages)
- ✓ DETECT-01 through DETECT-06 — v3.0 (gsd-core detection, parsing, GSD-2 removal)
- ✓ DOCS-01 through DOCS-08 — v3.0 (all document types surfaced)
- ✓ PROG-01 through PROG-03 — v3.0 (progress metrics)
- ✓ VIS-01 through VIS-04 — v3.0 (requirements traceability, waves, archives, gap highlighting)

#### Active

(None — awaiting next milestone definition)

#### Out of Scope

- Writing to project files — App is read-only by design constraint
- gsd-core workflow execution — Monitor is a viewer, not a workflow runner
- Cross-project dependency visualization — High complexity, not core to monitoring value
- Mobile/macOS/Linux — Windows-only (Edge WebView2)

## Constraints

- **Tech stack**: Python 3.11+ / FastAPI / pywebview / React 19 / Tailwind CSS v4 / Vite 6 — no stack changes
- **Platform**: Windows only (Edge WebView2)
- **Settings**: Must remain compatible with `%LOCALAPPDATA%\WinGSDMonitor\settings.json` PascalCase format
- **Read-only**: App never writes to project files

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Deduplicate by canonical repo root (resolve `.git` file -> main worktree) | Worktrees share the same `.planning/` — showing duplicates is the primary complaint | ✓ Phase 01 |
| VS Code dark theme | User explicitly requested; familiar to target audience | ✓ Phase 02 |
| All `.planning/` files browsable (not just a curated subset) | User wants full access; curated defaults (ROADMAP/STATE/PLAN) shown first | ✓ Phase 03 |
| Non-blocking trylock for FS watcher refreshes | Drop duplicate events instead of queuing them — eliminates redundant rescans | ✓ Phase 04 |
| `os.walk` + `_EXCLUDED_DIRS` for discovery | Skip `node_modules`/`.venv`/`.git`/`build`/`dist` — eliminates slow scans on large repos | ✓ Phase 04 |
| `StateParser` wired into discovery pipeline | `STATE.md` current position is now authoritative active phase name on dashboard | ✓ Phase 04 |
| FastAPI lifespan context manager | Replace deprecated `@on_event` decorators — eliminates deprecation warnings | ✓ Phase 06 |
| `_compute_drift` with injectable `now` | Real drift computation; injectable `now` enables deterministic TDD | ✓ Phase 09 |
| config.json as primary gsd-core detection signal | ROADMAP.md heading sniff as fallback; config.json is authoritative | ✓ Phase 11 |
| Boolean flags for new doc types (has_ui_spec, etc.) | Consistent with existing has_context/has_plan pattern | ✓ Phase 11 |
| StateParser 3-variant progress extraction | YAML frontmatter first, bold-inline, then pipe-table — covers all STATE.md formats | ✓ Phase 11 |
| Fetch-once display-from-cache for InsightsPage | Fetch on segment change, not tab switch — avoids redundant API calls | ✓ Phase 12 |
| v3.0 section-bounded requirement parsing | RequirementsParser scans only ## v3.0 section, excludes Validated/Future sections | ✓ Phase 12 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-18 after v3.0 milestone*
