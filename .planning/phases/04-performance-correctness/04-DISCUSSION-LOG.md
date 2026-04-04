# Phase 4: Performance & Correctness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 04-performance-correctness
**Areas discussed:** Scan exclusion list, StateParser field wiring, Trylock pending pattern, WS event differentiation

---

## Scan Exclusion List

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded constants | Fixed list in project_discovery.py — fast, no UI needed, covers 99% of cases | ✓ |
| User-configurable in settings | Add exclude_dirs to AppSettings and SettingsPage — more flexible but more complexity | |

**User's choice:** Hardcoded constants

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, exclude .git/ | Also skip .git directories — large and never contain .planning/ or .gsd/ | ✓ |
| No, leave .git/ traversable | Stick exactly to the 4 dirs in REQUIREMENTS.md | |

**User's choice:** Yes, exclude .git/
**Notes:** Final exclusion set: `node_modules`, `.venv`, `.git`, `build`, `dist`

---

## StateParser Field Wiring

| Option | Description | Selected |
|--------|-------------|----------|
| STATE.md overrides ROADMAP | Wire StateParser; use status/active_slice as authoritative current position. Falls back to ROADMAP in_progress if STATE.md absent. | ✓ |
| ROADMAP remains authoritative | Wire StateParser for extra fields only; active phase name still from ROADMAP phases | |

**User's choice:** STATE.md overrides ROADMAP

| Option | Description | Selected |
|--------|-------------|----------|
| Just active phase / current position | Use status text or active_slice — one indicator on dashboard | ✓ |
| All fields passed through to API | Add all StateInfo fields to SegmentModel/SegmentPayload | |

**User's choice:** Just active phase / current position
**Notes:** Single `state_current_position: str | None` field on SegmentModel; minimal schema surface

---

## Trylock Pending Pattern

| Option | Description | Selected |
|--------|-------------|----------|
| Drop-only, no pending | Pure coalescing — if busy, drop entirely. Matches PROJECT.md 'drop not queue'. | ✓ |
| Drop + one pending flag | Set flag so one re-scan runs after current completes. Guarantees last change reflected. | |

**User's choice:** Drop-only, no pending

---

## WS Event Differentiation

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, fix C-04 here too | Check event type: projects_updated → reload(); settings_saved → no reload. Prevents double reload. | ✓ |
| No, just fix the race (PERF-04 only) | Remove reload() from save(), leave context.tsx always-reload. C-04 deferred. | |

**User's choice:** Yes, fix C-04 here too

---

## Claude's Discretion

- Exact field name for state current position on SegmentModel
- Whether to add to SegmentPayload in api.ts or use existing shape
- Test coverage additions for exclusion logic

## Deferred Ideas

None.
