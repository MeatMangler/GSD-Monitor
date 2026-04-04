# Roadmap: GSD Monitor

## Overview

GSD Monitor already has a working Python/FastAPI/React skeleton — these phases fix what is broken and add what is missing. Phase 1 eliminates the duplicate-project problem (the #1 user complaint), Phase 2 replaces the visual structure with one that makes status legible at a glance, Phase 3 adds the doc browser so every planning file is readable from within the app, and Phase 4 closes the backend correctness and performance gaps that remain.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Worktree Deduplication** - Fix the backend so each canonical repo appears exactly once, with a worktree badge
- [x] **Phase 2: Visual Redesign** - VS Code dark theme, stats bar, phase list, breadcrumb
- [x] **Phase 3: Doc Browser** - Full `.planning/` file tree navigation with inline markdown rendering
- [x] **Phase 4: Performance & Correctness** - Non-blocking lock, scan exclusions, StateParser wiring, settings race fix
- [x] **Phase 5: GSD-2 StateParser Wiring** - Wire StateParser into GSD-2 discovery path so stateCurrentPosition is populated for GSD-2 projects (completed 2026-04-04)
- [x] **Phase 6: Tech Debt Remediation** - Fix stale REQUIREMENTS.md checkboxes, tick 03-VERIFICATION.md UAT items, upgrade FastAPI lifespan pattern
- [x] **Phase 7: Frontend Source Completion & Bundle Rebuild** - Merge missing source files to master, create stubs for v2 placeholders, rebuild frontend/dist (completed 2026-04-04)
- [x] **Phase 8: Phase 01 Verification & Metadata Cleanup** - Write Phase 01 VERIFICATION.md to close orphaned WRKTR requirements, fix stale planning metadata, fix Python deprecation

## Phase Details

### Phase 1: Worktree Deduplication
**Goal**: Each git repo appears exactly once in the project dropdown, regardless of how many worktrees are checked out
**Depends on**: Nothing (first phase)
**Requirements**: WRKTR-01, WRKTR-02, WRKTR-03, WRKTR-04, WRKTR-05
**Success Criteria** (what must be TRUE):
  1. Opening a repo that has three worktrees checked out shows one dropdown entry, not three
  2. That single entry has a badge showing the worktree count (e.g., "3 worktrees")
  3. Hovering or clicking the badge reveals the branch/directory names of each worktree
  4. One worktree in the list is marked as currently active (the currently-checked-out one)
  5. The deduplication logic reads the `.git` file pointer — not heuristics — to resolve canonical repo root
**Plans**: 2 plans
Plans:
- [x] 01-01-PLAN.md — Backend worktree detection, deduplication in discover_groups, API serialization
- [x] 01-02-PLAN.md — Frontend WorktreeInfo interface, badge + CSS-only hover tooltip
**Status**: Complete — verified 2026-04-04

### Phase 2: Visual Redesign
**Goal**: The dashboard immediately communicates project status without any navigation or clicks, using a VS Code dark aesthetic
**Depends on**: Phase 1
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04
**Success Criteria** (what must be TRUE):
  1. Opening the app to any project shows % complete, phases done/total, and active phase name without scrolling
  2. All phases are visible in a list with color-coded status indicators (green=done, blue=active, gray=todo) on the main view
  3. A breadcrumb reading "repo → project → active phase" is always visible at the top
  4. The entire UI renders with a dark background (#1e1e1e range), matching sidebar, and VS Code-style typography
**Plans**: 2 plans
Plans:
- [x] 02-01-PLAN.md — DashboardPage stats bar, breadcrumb, phase row borders, VS Code tokens + index.css font
- [x] 02-02-PLAN.md — ShellLayout sidebar VS Code token swaps
**UI hint**: yes

### Phase 3: Doc Browser
**Goal**: Any file in the project's `.planning/` directory is navigable and readable inline without leaving the app
**Depends on**: Phase 2
**Requirements**: DASH-05, DASH-06, DASH-07
**Success Criteria** (what must be TRUE):
  1. A file tree panel shows all files and folders inside `.planning/` for the selected project
  2. Clicking any markdown file renders it inline as formatted HTML (not raw text)
  3. ROADMAP.md, STATE.md, the active PLAN.md, and REQUIREMENTS.md appear as prominent quick-access shortcuts
  4. Navigating the file tree does not require any page reload or full re-fetch
**Plans**: 2 plans
Plans:
- [x] 03-01-PLAN.md — Backend doc tree/file endpoints, frontend API client, route + nav wiring
- [x] 03-02-PLAN.md — DocsPage two-column layout with tree panel, quick-access, markdown rendering
**UI hint**: yes

### Phase 4: Performance & Correctness
**Goal**: The backend is fast, correct, and non-blocking — scans stay tight, state is fully populated, and the UI never flashes stale data
**Depends on**: Phase 3
**Requirements**: PERF-01, PERF-02, PERF-03, PERF-04
**Success Criteria** (what must be TRUE):
  1. Saving settings shows updated project data driven only by the WebSocket event — no stale-data flash before it arrives
  2. A file-system change during an active scan is dropped (coalesced), not queued — no cascade of redundant re-scans
  3. Scanning a directory tree that contains `node_modules/`, `.venv/`, `build/`, or `dist/` completes noticeably faster than before
  4. The active phase name on the dashboard matches what STATE.md reports as the current position
**Plans**: 2 plans
Plans:
- [x] 04-01-PLAN.md — Non-blocking trylock, scan exclusions, settings save race fix
- [x] 04-02-PLAN.md — StateParser wiring into discovery pipeline and dashboard display

### Phase 5: GSD-2 StateParser Wiring
**Goal**: GSD-2 projects show the correct active phase from STATE.md, not just the fallback in-progress roadmap phase
**Depends on**: Phase 4
**Requirements**: PERF-03 (GSD-2 path)
**Gap Closure**: Closes PERF-03 partial gap and Flow 4 integration gap from audit
**Success Criteria** (what must be TRUE):
  1. `_discover_gsd2()` calls `StateParser.parse()` before constructing `SegmentModel`
  2. `state_current_position` is populated on GSD-2 segments when STATE.md exists
  3. DashboardPage displays STATE.md active phase for GSD-2 projects (same as GSD-1 behavior)
**Plans**: 1 plan
Plans:
- [x] 05-01-PLAN.md — Wire StateParser.parse() into _discover_gsd2() with GSD-2 field priority + unit tests

### Phase 6: Tech Debt Remediation
**Goal**: Documentation and code hygiene — stale checkboxes corrected, UAT items ticked, FastAPI deprecation removed
**Depends on**: Phase 5
**Requirements**: WRKTR-03, WRKTR-04, PERF-01, PERF-02, PERF-04 (checkbox/traceability fixes), DASH-06 (UAT tick)
**Gap Closure**: Closes all tech debt items from audit
**Success Criteria** (what must be TRUE):
  1. REQUIREMENTS.md checkboxes for WRKTR-03, WRKTR-04, PERF-01, PERF-02, PERF-04 are `[x]`
  2. Traceability table shows Complete for those 5 requirements
  3. `03-VERIFICATION.md` UAT items are checked off
  4. `app.py` uses lifespan context manager instead of deprecated `@on_event`
**Plans**: 2 plans
Plans:
- [x] 06-01-PLAN.md — Fix stale checkboxes in 03-VERIFICATION.md and REQUIREMENTS.md traceability
- [x] 06-02-PLAN.md — Migrate app.py from deprecated @on_event to lifespan context manager

### Phase 7: Frontend Source Completion & Bundle Rebuild
**Goal**: Master branch has a complete, compilable frontend source tree and a fresh dist bundle that reflects all Phase 02-05 work
**Depends on**: Phase 6
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07, PERF-03, PERF-04 (currently broken in source/bundle)
**Gap Closure**: Closes INT-01 (missing source files) and INT-02 (stale bundle) from v1.0 audit
**Success Criteria** (what must be TRUE):
  1. `context.tsx` and `SettingsPage.tsx` exist in `frontend/src/` on master (merged from worktree-agent-a9b06372)
  2. Placeholder stub components exist for `DriftPage.tsx`, `QuickTasksPage.tsx`, `VerificationPage.tsx`
  3. `tsc -b` completes with zero errors
  4. `npm run build` produces a fresh `frontend/dist` bundle
  5. Bundle contains DocsPage, AppProvider, stateCurrentPosition, and ReactMarkdown rendering
**Plans**: 2 plans
Plans:
- [x] 07-01-PLAN.md — Reconstruct config files, cherry-pick context.tsx + SettingsPage.tsx, create Drawer + stub pages
- [x] 07-02-PLAN.md — Build frontend bundle and verify Phase 02-05 features in output

### Phase 8: Phase 01 Verification & Metadata Cleanup
**Goal**: Close all remaining documentation gaps — Phase 01 VERIFICATION.md written, planning metadata current, Python deprecation fixed
**Depends on**: Phase 7
**Requirements**: WRKTR-01, WRKTR-02, WRKTR-05 (orphaned — need verification artifact)
**Gap Closure**: Closes WRKTR-01/02/05 orphaned status, Phase 06 stale metadata, Python deprecation warning
**Success Criteria** (what must be TRUE):
  1. `phases/01-worktree-deduplication/01-VERIFICATION.md` exists and documents WRKTR-01, WRKTR-02, WRKTR-05 with code evidence
  2. ROADMAP.md Phase 6 checkbox is `[x]` and progress table shows Complete
  3. STATE.md reflects Phase 6 completion (stopped_at updated, completed_plans accurate)
  4. `datetime.utcfromtimestamp()` replaced with timezone-aware equivalent in `project_discovery.py`
**Plans**: 2 plans
Plans:
- [x] 08-01-PLAN.md — Write Phase 01 VERIFICATION.md and update REQUIREMENTS.md
- [x] 08-02-PLAN.md — Fix stale metadata and Python datetime deprecation

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Worktree Deduplication | 2/2 | Complete | 2026-04-04 |
| 2. Visual Redesign | 2/2 | Complete | 2026-04-03 |
| 3. Doc Browser | 2/2 | Complete | 2026-04-04 |
| 4. Performance & Correctness | 2/2 | Complete | 2026-04-04 |
| 5. GSD-2 StateParser Wiring | 1/1 | Complete | 2026-04-04 |
| 6. Tech Debt Remediation | 2/2 | Complete | 2026-04-04 |
| 7. Frontend Source Completion & Bundle Rebuild | 2/2 | Complete   | 2026-04-04 |
| 8. Phase 01 Verification & Metadata Cleanup | 2/2 | Complete | 2026-04-04 |
