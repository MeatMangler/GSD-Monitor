# Roadmap: GSD Monitor

## Milestones

- [x] **v1.0** — Worktree deduplication, VS Code dark dashboard, doc browser, performance & correctness, GSD-2 StateParser wiring, FastAPI modernization, frontend source rebuild (8 phases, 15 plans, 2026-04-03 → 2026-04-04) — [Archive](milestones/v1.0-ROADMAP.md)
- [ ] **v2.0 Feature Pages** — Real drift computation, Drift page, Quick Tasks page, Verification page (2 phases)

---

## v2.0 — Feature Pages

### Phases

- [x] **Phase 9: Drift Computation** - Backend computes real DriftIndicator values from plan age and phase status (completed 2026-04-12)
- [x] **Phase 10: Feature Pages** - Drift, Quick Tasks, and Verification pages wired to live API data (completed 2026-04-12)

---

## Phase Details

### Phase 9: Drift Computation
**Goal**: The backend produces accurate DriftIndicator values for every phase based on plan write time, last updated date, and phase status — replacing the hardcoded DEFERRED placeholder
**Depends on**: Nothing (pure backend change)
**Requirements**: DRFT-01
**Success Criteria** (what must be TRUE):
  1. A phase with no plan file and NOT_STARTED status returns DriftIndicator.DEFERRED
  2. A phase with a plan file last updated more than 30 days ago returns DriftIndicator.MAJOR
  3. A phase with a plan file last updated 7–30 days ago returns DriftIndicator.MINOR
  4. A completed phase with recent activity returns DriftIndicator.NONE
**Plans:** 1/1 plans complete
Plans:
- [x] 09-01-PLAN.md — TDD: implement _compute_drift helper and wire into GSD-1/GSD-2 enrichment

### Phase 10: Feature Pages
**Goal**: The three stub pages — Drift, Quick Tasks, and Verification — display real data from the existing API, giving users an actionable view of phase health, task status, and validation coverage
**Depends on**: Phase 9
**Requirements**: DRFT-02, DRFT-03, DRFT-04, DRFT-05, QTSK-01, QTSK-02, QTSK-03, QTSK-04, QTSK-05, VERIF-01, VERIF-02, VERIF-03, VERIF-04
**Success Criteria** (what must be TRUE):
  1. DriftPage shows a per-phase table sorted MAJOR first, with color-coded badges and plan age, and un-started phases collapsed behind a toggle
  2. QuickTasksPage fetches and renders all quick tasks for the active project with color-coded status badges, sorted by last_updated descending, with an empty state when none exist
  3. VerificationPage shows a per-phase summary with has_validation, nyquist_compliant, and has_uat columns, and clicking a row expands inline validation content rendered as markdown
  4. Phases without a validation file are dimmed and hidden behind a toggle on the Verification page
**Plans:** 3/3 plans complete
Plans:
- [x] 10-01-PLAN.md — Extract shared utils, add plan_write_time to PhasePayload, implement DriftPage
- [x] 10-02-PLAN.md — Implement QuickTasksPage with fetch, sort, badges, and empty state
- [x] 10-03-PLAN.md — Implement VerificationPage with badges, inline expand, and collapsible section
**UI hint**: yes

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 9. Drift Computation | 1/1 | Complete   | 2026-04-12 |
| 10. Feature Pages | 3/3 | Complete   | 2026-04-12 |
