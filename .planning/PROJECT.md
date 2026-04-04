# GSD Monitor

## What This Is

GSD Monitor is a Windows desktop companion app (Python + pywebview + React) that discovers GSD projects on disk and gives developers an immediate visual overview of every GSD workflow document. It scans configured directories, classifies GSD-1 (`.planning/`) and GSD-2 (`.gsd/`) projects, and surfaces roadmap phases, planning docs, and project status through a local FastAPI + React UI rendered in Edge WebView2.

## Core Value

A developer opens GSD Monitor and within seconds understands exactly where every project stands — which phases are done, what's active, and can read any planning doc — with zero duplicate entries and zero confusion about which project they're looking at.

## Requirements

### Validated

- [x] Project dropdown shows exactly ONE entry per canonical repo, regardless of how many git worktrees exist — *Validated in Phase 01: worktree-deduplication*
- [x] Worktree count shown as a badge on the project entry when multiple worktrees exist — *Validated in Phase 01: worktree-deduplication*

### Active

- [x] Stats bar visible immediately above fold: % complete, phases done/total, active phase name — *Validated in Phase 02: visual-redesign*
- [x] Phase list with clear status colors (done/active/todo) visible without clicking — *Validated in Phase 02: visual-redesign*
- [x] Breadcrumb always shows: repo → project → active phase — *Validated in Phase 02: visual-redesign*
- [x] VS Code dark visual theme throughout (sidebar, content area, typography) — *Validated in Phase 02: visual-redesign*
- [x] Doc browser navigates the full `.planning/` file tree — *Validated in Phase 03: doc-browser*
- [x] ROADMAP.md, STATE.md, active PLAN.md, and REQUIREMENTS.md all renderable — *Validated in Phase 03: doc-browser*
- [x] App feels fast — no sluggish scanning or UI blocking — *Validated in Phase 04: performance-correctness*

### Out of Scope

- Editing or writing any GSD markdown files from within the app
- macOS/Linux support — Windows + WebView2 only
- Multi-user or cloud sync
- Replacing the GSD CLI or Claude Code

## Context

The codebase already exists with a working Python/FastAPI backend and React frontend. Previous revisions failed on four dimensions: worktree duplicates (same project appeared once per worktree directory), poor visual quality, slow scanning, and wrong/missing docs shown. The visual structure gave no clarity — no phase list above the fold, no breadcrumb, no summary stats. The backend has multiple known bugs documented in `.planning/codebase/CONCERNS.md`.

**Key technical facts:**
- Git worktrees have `.git` as a FILE (not a directory) pointing back to the main repo via `gitdir:` — this is how to detect and deduplicate them
- The `RuntimeState._refresh_lock` is a blocking lock (not coalescing) — causes queued redundant rescans
- `StateParser` exists but is never called — active phase context is lost
- Discovery traverses `node_modules/` and `.venv/` causing slow scans
- Frontend settings save has a race condition causing stale-data flash

## Constraints

- **Tech stack**: Python 3.11+ / FastAPI / pywebview / React 19 / Tailwind CSS v4 / Vite 6 — no stack changes
- **Platform**: Windows only (Edge WebView2)
- **Settings**: Must remain compatible with `%LOCALAPPDATA%\WinGSDMonitor\settings.json` PascalCase format
- **Read-only**: App never writes to project files

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Deduplicate by canonical repo root (resolve `.git` file → main worktree) | Worktrees share the same `.planning/` — showing duplicates is the primary complaint | ✓ Phase 01 |
| VS Code dark theme | User explicitly requested; familiar to target audience | — Pending |
| All `.planning/` files browsable (not just a curated subset) | User wants full access; curated defaults (ROADMAP/STATE/PLAN) shown first | — Pending |
| Non-blocking trylock for FS watcher refreshes | Drop duplicate events instead of queuing them — eliminates redundant rescans | ✓ Phase 04 |
| `os.walk` + `_EXCLUDED_DIRS` for discovery | Skip `node_modules`/`.venv`/`.git`/`build`/`dist` — eliminates slow scans on large repos | ✓ Phase 04 |
| `StateParser` wired into discovery pipeline | `STATE.md` current position is now authoritative active phase name on dashboard | ✓ Phase 04 |
| Settings save no longer triggers reload | WS handler filters on `projects_updated` type — prevents stale-data flash after settings save | ✓ Phase 04 |
| `StateParser` wired into GSD-2 discovery | GSD-2 segments now surface `active_slice` as `stateCurrentPosition` — closes PERF-03 GSD-2 gap | ✓ Phase 05 |
| FastAPI lifespan context manager | Replace deprecated `@on_event` decorators — eliminates deprecation warnings and future breakage risk | ✓ Phase 06 |

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
*Last updated: 2026-04-04 — Phase 07 complete (frontend-source-completion) — fresh bundle built with all Phase 02-05 features*
