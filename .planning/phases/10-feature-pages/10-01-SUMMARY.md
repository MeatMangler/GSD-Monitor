---
phase: 10-feature-pages
plan: "01"
subsystem: frontend
tags: [react, typescript, drift, utils, tailwind]
requires: []
provides:
  - "frontend/src/utils.ts — shared fmtDate, statusLabel, byLastUpdated, statusBorderClass helpers"
  - "frontend/src/pages/DriftPage.tsx — full per-phase drift detection page"
affects:
  - "frontend/src/pages/DashboardPage.tsx — now imports from utils.ts instead of inline definitions"
  - "frontend/src/api.ts — PhasePayload extended with plan_write_time field"
tech-stack:
  added: []
  patterns:
    - "Shared utils module pattern — helpers extracted from page components into src/utils.ts"
    - "DRIFT_ORDER map pattern — sort priority via Record<string, number> constant"
    - "Collapsible deferred section — useState toggle with aria-expanded/aria-controls"
key-files:
  created:
    - frontend/src/utils.ts
  modified:
    - frontend/src/api.ts
    - frontend/src/pages/DashboardPage.tsx
    - frontend/src/pages/DriftPage.tsx
key-decisions:
  - "Used plan_write_time Option A (add field to PhasePayload interface) — field already serialized by backend, zero backend changes needed"
  - "Placed DRIFT_ORDER as module-level constant to avoid useMemo exhaustive-deps lint warning"
  - "Used <div> not <button> for drift rows — rows are non-clickable per UI-SPEC"
requirements-completed:
  - DRFT-02
  - DRFT-03
  - DRFT-04
  - DRFT-05
metrics:
  duration: "1 min"
  completed: "2026-04-12"
  tasks: 2
  files: 4
---

# Phase 10 Plan 01: Shared Utils Extraction and DriftPage Summary

Extracted four shared helper functions from DashboardPage into `frontend/src/utils.ts`, added `plan_write_time` to the TypeScript `PhasePayload` interface, and implemented the full `DriftPage` with per-phase drift table sorted MAJOR-first, color-coded drift badges, plan age in days, and a collapsible deferred phases section.

**Duration:** 1 min | **Started:** 2026-04-12T09:39:40Z | **Completed:** 2026-04-12T09:41:15Z | **Tasks:** 2/2 | **Files:** 4

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Extract shared utils and add plan_write_time to PhasePayload | `7c5c746` | utils.ts (created), api.ts, DashboardPage.tsx |
| 2 | Implement DriftPage with full drift table | `0200aae` | DriftPage.tsx |

## What Was Built

### frontend/src/utils.ts (new)

Shared utility module with four exported functions previously defined inline in DashboardPage.tsx:

- `byLastUpdated` — sort comparator: most recently updated first, then by phase number descending
- `fmtDate` — formats ISO date strings to "Mon D, YYYY" locale format, returns "—" for null/undefined
- `statusLabel` — maps status enum strings to human-readable labels
- `statusBorderClass` — maps status to left-accent border color Tailwind class

### frontend/src/api.ts

Added `plan_write_time?: string | null` to `PhasePayload` interface (after `last_updated`). The field was already serialized by the FastAPI backend via `model_dump_json()` from the Pydantic `PhaseEntry` model added in Phase 9. Zero backend changes required.

### frontend/src/pages/DashboardPage.tsx

Removed four inline function definitions and replaced with a single import from `../utils`. Component behavior is identical.

### frontend/src/pages/DriftPage.tsx

Full implementation replacing the stub. Key behaviors:

- **Sort order:** MAJOR (0) → MINOR (1) → NONE (2) → DEFERRED (3) via `DRIFT_ORDER` constant map
- **Phase rows:** non-clickable `<div>` per UI-SPEC; shows phase number (zero-padded), title, status label, drift badge, plan age in days, last updated date
- **Drift badges:** MAJOR=`bg-red-900/40 text-red-400`, MINOR=`bg-yellow-900/40 text-yellow-400`, NONE=`bg-green-900/40 text-[#4ec994]`, DEFERRED=`bg-[#2a2d2e] text-[#858585]`
- **Plan age:** computed via `planAgeDays(p.plan_write_time)` — "N days" or "—" when absent
- **Deferred section:** phases with `status === "not_started" && drift === "deferred"` hidden behind toggle button with `aria-expanded` and `aria-controls="deferred-phases"`; revealed rows at `opacity-60`
- **Guards:** loading state (`p-6`), no-project state (`p-6`), empty state message

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — DriftPage is fully implemented with live data from context.

## Threat Flags

None — no new network endpoints, auth paths, or trust boundary changes introduced. DriftPage is purely a read-only render of data already in React context.

## Self-Check: PASSED

- [x] `frontend/src/utils.ts` exists on disk
- [x] `frontend/src/pages/DriftPage.tsx` exists on disk (rewritten from stub)
- [x] Commit `7c5c746` exists: `feat(10-01): extract shared utils and add plan_write_time to PhasePayload`
- [x] Commit `0200aae` exists: `feat(10-01): implement DriftPage with drift table, badges, and collapsible deferred section`
- [x] `npx tsc -b --noEmit` exits 0

## Next

Ready for 10-02 (QuickTasksPage) and 10-03 (VerificationPage).
