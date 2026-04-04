# Phase 4: Performance & Correctness - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Four targeted backend/frontend correctness fixes: non-blocking trylock for the FS watcher (PERF-01), scan directory exclusions (PERF-02), StateParser wired into discovery (PERF-03), and settings save race fix (PERF-04). No new pages, no new routes, no UI redesign — these are correctness and performance patches to existing code.

</domain>

<decisions>
## Implementation Decisions

### Scan Exclusions (PERF-02)
- **D-01:** Exclusion list is **hardcoded constants** in `project_discovery.py` — not user-configurable in settings. No UI change needed.
- **D-02:** Excluded directory names: `node_modules`, `.venv`, `.git`, `build`, `dist`. The `.git/` directory is explicitly included in the list (it is large and can never contain `.planning/` or `.gsd/` sub-dirs).
- **D-03:** Exclusion applied in `_find_dirs` — prune matching directory names before `rglob` descends into them (i.e., use `os.walk` with a topdown pruning approach, or filter out results whose path components include excluded names).

### StateParser Wiring (PERF-03)
- **D-04:** `StateParser.parse()` is called during segment construction for each segment that has a resolvable `STATE.md` / `state.md`.
- **D-05:** STATE.md overrides ROADMAP-derived active phase: the `status` text (from the "Current Position" section) or `active_slice` field from `StateInfo` is the authoritative "current position" displayed on the dashboard. Falls back to ROADMAP `in_progress` phase title if STATE.md is absent, empty, or returns no status.
- **D-06:** Only the current position / active phase text is surfaced — no new fields added to `SegmentModel` beyond what's needed to pass the active phase name. Keep the schema surface minimal. A single `state_current_position: str | None` field (or equivalent) on `SegmentModel` is sufficient.

### Trylock / FS Watcher (PERF-01)
- **D-07:** `_refresh_lock` is changed to a **non-blocking trylock**: `_refresh_lock.acquire(blocking=False)`. If acquire fails (scan in progress), the incoming FS event is **dropped entirely** — no pending flag, no re-queue.
- **D-08:** Pure drop-only coalescing: next real FS change will trigger a fresh scan. Matches PROJECT.md decision: "drop, not queue."

### Settings Save Race Fix (PERF-04 + C-04)
- **D-09:** `SettingsPage.save()` removes the `await reload()` call. The function saves settings and updates local message state — nothing else. The WebSocket `projects_updated` event drives the data refresh.
- **D-10:** `context.tsx` WS handler is upgraded to check event type: `projects_updated` → call `reload()`; `settings_saved` → do **not** call `reload()` (prevents double reload on save). This closes C-04 while we're touching the WS handler.

### Claude's Discretion
- Exact field name for the new state current position on `SegmentModel` (`state_current_position` vs. `active_state_text` or similar)
- Whether to also add `state_current_position` to the API JSON response via `SegmentPayload` in `api.ts`, or use the existing `activeSegment` shape
- Test coverage additions (if any) for the new exclusion logic

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Performance & Correctness — PERF-01, PERF-02, PERF-03, PERF-04 define acceptance criteria
- `.planning/ROADMAP.md` §Phase 4 — Success criteria 1–4

### Backend files to modify
- `gsd_monitor/api/app.py` — `RuntimeState._on_fs_change` and `RuntimeState.refresh()` for PERF-01 trylock; no other app.py changes expected
- `gsd_monitor/services/project_discovery.py` — `_find_dirs()` for PERF-02 exclusions; segment construction for PERF-03 StateParser wiring
- `gsd_monitor/parsers/state_parser.py` — reference only (already implemented); do NOT modify
- `gsd_monitor/models/core.py` — add `state_current_position: str | None` (or equivalent) to `SegmentModel` for PERF-03

### Frontend files to modify
- `frontend/src/pages/SettingsPage.tsx` — remove `await reload()` from `save()` (PERF-04)
- `frontend/src/context.tsx` — upgrade WS `onmessage` handler to check event type (C-04/D-10)
- `frontend/src/api.ts` — add `stateCurrentPosition?: string` to `SegmentPayload` interface if PERF-03 exposes the field

### Existing concerns to close
- `.planning/codebase/CONCERNS.md` §C-03 — settings save race (PERF-04)
- `.planning/codebase/CONCERNS.md` §C-04 — WS event type ignored (D-10)
- `.planning/codebase/CONCERNS.md` §C-06 — blocking lock (PERF-01)
- `.planning/codebase/CONCERNS.md` §M-03 — StateParser unused (PERF-03)
- `.planning/codebase/CONCERNS.md` §M-04 — `_find_dirs` no exclusions (PERF-02)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `StateParser.parse(file_path: str) -> ParseResult` — fully implemented in `gsd_monitor/parsers/state_parser.py`; returns `StateInfo` with `active_milestone`, `active_slice`, `active_task`, `workflow_phase`, `status` fields. Only needs to be called.
- `threading.Lock()` at `app.py:58` — replace acquire pattern with `acquire(blocking=False)` + early return
- `SegmentModel` in `gsd_monitor/models/core.py` — add one nullable field for state current position

### Established Patterns
- `_find_dirs` uses `root.rglob(name)` — the fix should prune excluded dir names during traversal (either switch to `os.walk` with topdown pruning, or post-filter by checking all path parts against the exclusion set)
- Segment construction happens in `_build_gsd1_segment` and `_build_gsd2_segment` in `project_discovery.py` — StateParser call goes here, reading from `ctx.planning_base / "STATE.md"` (and falling back to `state.md`)
- WebSocket message format: `{"type": "projects_updated"}` and `{"type": "settings_saved"}` — `context.tsx` currently ignores `.type` entirely

### Integration Points
- `_on_fs_change` → `self.refresh()` — the trylock change goes here: try `_refresh_lock.acquire(blocking=False)`, if False return immediately
- Dashboard `activePhaseName` derived in `DashboardPage.tsx` from ROADMAP phases — after PERF-03, this should prefer `activeSegment.stateCurrentPosition` if present
- `SettingsPage.save()` lines 26–30 — remove `await reload()` (line 29)

</code_context>

<specifics>
## Specific Ideas

- For `_find_dirs` exclusion: the cleanest approach is to switch from `root.rglob(name)` to `os.walk(root, topdown=True)` and prune `dirnames` in-place when any dir name is in `_EXCLUDED_DIRS`. This avoids descending into excluded trees entirely (rglob still traverses them even if results are filtered).
- The `_EXCLUDED_DIRS` constant set: `{"node_modules", ".venv", ".git", "build", "dist"}` — screaming snake case per codebase convention.
- For StateParser wiring: `StateParser.parse(str(planning_base / "STATE.md"))` — if `ParseResult.ok` and `StateInfo.status` or `StateInfo.active_slice` is non-empty, use that as `state_current_position`.
- Dashboard override: in `DashboardPage.tsx` stats memo, check `activeProject` segments for `stateCurrentPosition` before falling back to ROADMAP `in_progress` phase title.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-performance-correctness*
*Context gathered: 2026-04-04*
