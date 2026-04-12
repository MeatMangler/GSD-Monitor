# GSD Monitor

## What This Is

GSD Monitor is a Windows desktop companion app (Python + pywebview + React) that discovers GSD projects on disk and gives developers an immediate visual overview of every GSD workflow document. It scans configured directories, classifies GSD-1 (`.planning/`) and GSD-2 (`.gsd/`) projects, and surfaces roadmap phases, planning docs, and project status through a local FastAPI + React UI rendered in Edge WebView2.

## Core Value

A developer opens GSD Monitor and within seconds understands exactly where every project stands — which phases are done, what's active, and can read any planning doc — with zero duplicate entries and zero confusion about which project they're looking at.

## Current State (v1.0 — Shipped 2026-04-04)

All 16 v1 requirements delivered across 8 phases:

- **Worktree deduplication**: One entry per canonical repo, worktree badge + hover tooltip
- **VS Code dark dashboard**: Stats bar, breadcrumb, color-coded phase list above the fold
- **Doc browser**: Full `.planning/` file tree with inline markdown rendering; quick-access for ROADMAP, STATE, PLAN, REQUIREMENTS
- **Performance**: Non-blocking FS watcher coalescing, `node_modules`/`.venv`/`build`/`dist` excluded from scan
- **StateParser wired**: Active phase from `STATE.md` authoritative for both GSD-1 and GSD-2 projects
- **Modern stack**: FastAPI lifespan context manager, timezone-aware `datetime` throughout

**Tech debt carried to v2:** 7 items (0 critical) — see [v1.0 audit](.planning/v1.0-MILESTONE-AUDIT.md)

## Current Milestone: v2.0 Feature Pages

**Goal:** Surface the three stub pages — Drift, Quick Tasks, and Verification — with real data from the already-built backend.

**Target features:**
- Drift: Git-based staleness per phase (real commit dates vs plan write times), highlight drifted phases
- Quick Tasks: List all `quick/` tasks with status, title, dates; link to PLAN.md in doc browser
- Verification: Per-phase `has_validation`, Nyquist status, and validation content in a readable UI

## Constraints

- **Tech stack**: Python 3.11+ / FastAPI / pywebview / React 19 / Tailwind CSS v4 / Vite 6 — no stack changes
- **Platform**: Windows only (Edge WebView2)
- **Settings**: Must remain compatible with `%LOCALAPPDATA%\WinGSDMonitor\settings.json` PascalCase format
- **Read-only**: App never writes to project files

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Deduplicate by canonical repo root (resolve `.git` file → main worktree) | Worktrees share the same `.planning/` — showing duplicates is the primary complaint | ✓ Phase 01 |
| VS Code dark theme | User explicitly requested; familiar to target audience | ✓ Phase 02 |
| All `.planning/` files browsable (not just a curated subset) | User wants full access; curated defaults (ROADMAP/STATE/PLAN) shown first | ✓ Phase 03 |
| Non-blocking trylock for FS watcher refreshes | Drop duplicate events instead of queuing them — eliminates redundant rescans | ✓ Phase 04 |
| `os.walk` + `_EXCLUDED_DIRS` for discovery | Skip `node_modules`/`.venv`/`.git`/`build`/`dist` — eliminates slow scans on large repos | ✓ Phase 04 |
| `StateParser` wired into discovery pipeline | `STATE.md` current position is now authoritative active phase name on dashboard | ✓ Phase 04 |
| Settings save no longer triggers reload | WS handler filters on `projects_updated` type — prevents stale-data flash after settings save | ✓ Phase 04 |
| `StateParser` wired into GSD-2 discovery | GSD-2 segments now surface `active_slice` as `stateCurrentPosition` — closes PERF-03 GSD-2 gap | ✓ Phase 05 |
| FastAPI lifespan context manager | Replace deprecated `@on_event` decorators — eliminates deprecation warnings and future breakage risk | ✓ Phase 06 |
| `datetime.fromtimestamp(ts, tz=timezone.utc)` replaces `utcfromtimestamp()` | Python 3.12 deprecated `utcfromtimestamp` — timezone-aware replacement eliminates warnings across 9 call sites | ✓ Phase 08 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-12 — v2.0 milestone started*
