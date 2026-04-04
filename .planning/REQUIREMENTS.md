# Requirements: GSD Monitor

**Defined:** 2026-04-03
**Core Value:** Developer opens GSD Monitor and immediately understands every project's status with zero duplicate entries and zero confusion

## v1 Requirements

### Worktree Deduplication

- [x] **WRKTR-01**: Project dropdown shows exactly one entry per canonical repo root (`.git` directory), regardless of how many worktrees exist
- [x] **WRKTR-02**: App detects git worktrees by checking if `.git` is a file (not a directory) and reads the `gitdir:` pointer to resolve the canonical repo root
- [x] **WRKTR-03**: Project entry in dropdown shows a badge with the count of active worktrees when more than one exists
- [x] **WRKTR-04**: Hovering or clicking the badge shows the list of worktree branch/directory names
- [x] **WRKTR-05**: An indicator marks which worktree is currently active (checked out)

### Dashboard & Visual

- [x] **DASH-01**: Stats bar is visible immediately above the fold: % complete, phases done/total, active phase name
- [x] **DASH-02**: Phase list shows all phases with status colors (done=green, active=blue, todo=gray) without any click required
- [x] **DASH-03**: Breadcrumb is always visible: repo name → project name → active phase
- [x] **DASH-04**: UI uses VS Code dark theme: dark background (#1e1e1e range), sidebar, matching typography and contrast
- [x] **DASH-05**: Doc browser panel shows `.planning/` file tree and renders selected markdown inline
- [x] **DASH-06**: ROADMAP.md, STATE.md, active PLAN.md, and REQUIREMENTS.md are surfaced as default quick-access files
- [x] **DASH-07**: Any file in `.planning/` is navigable and renderable in the doc browser

### Performance & Correctness

- [x] **PERF-01**: FS watcher uses non-blocking trylock — incoming events are dropped (coalesced) if a refresh is already in progress, not queued
- [x] **PERF-02**: Discovery excludes `node_modules/`, `.venv/`, `build/`, `dist/`, `.git/` directories from recursive scan
- [x] **PERF-03**: `StateParser` is wired into the discovery pipeline — active phase, active milestone, and workflow position are populated on each segment (GSD-1: complete; GSD-2: Phase 5 gap closure)
- [x] **PERF-04**: `SettingsPage.save()` does not call `reload()` after saving — relies solely on the WebSocket `projects_updated` event to refresh data

## v2 Requirements

### Drift Detection
- **DRIFT-01**: Actual drift computation using git commit dates vs phase write times
- **DRIFT-02**: Drift indicators show `none`/`minor`/`major` rather than always `deferred`

### Notifications
- **NOTIF-01**: Notify on phase completion (when enabled in settings)
- **NOTIF-02**: Notify on verification failure

### Verification Detail
- **VERIF-01**: Verification page lists per-phase detail — which phases need attention and why

## Out of Scope

| Feature | Reason |
|---------|--------|
| Editing markdown files | Read-only app by design; writing would require conflict resolution with Claude Code |
| macOS/Linux support | pywebview targets Edge WebView2; Windows-only per PRD |
| Multi-user or cloud sync | Single-user local tool |
| Replacing GSD CLI | Monitoring and visualization only |
| OAuth / auth system | No network exposure; loopback only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| WRKTR-01 | Phase 1 | Complete (01-01) |
| WRKTR-02 | Phase 1 | Complete (01-01) |
| WRKTR-03 | Phase 1 | Complete (01-02) |
| WRKTR-04 | Phase 1 | Complete (01-02) |
| WRKTR-05 | Phase 1 | Complete (01-01) |
| DASH-01 | Phase 2 | Complete |
| DASH-02 | Phase 2 | Complete |
| DASH-03 | Phase 2 | Complete |
| DASH-04 | Phase 2 | Complete |
| DASH-05 | Phase 3 | Complete |
| DASH-06 | Phase 3 | Complete (03-02) |
| DASH-07 | Phase 3 | Complete |
| PERF-01 | Phase 4 | Complete (04-01) |
| PERF-02 | Phase 4 | Complete (04-01) |
| PERF-03 (GSD-2) | Phase 5 | Complete (05-01) |
| PERF-04 | Phase 4 | Complete (04-01) |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0 ✓
- Satisfied: 16 (`[x]`), 0 pending

---
*Requirements defined: 2026-04-03*
*Last updated: 2026-04-04 — Phase 6 tech debt: all traceability items marked Complete*
