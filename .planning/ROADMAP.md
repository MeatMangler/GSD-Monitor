# Roadmap: GSD Monitor

## Milestones

- [x] **v1.0** — Worktree deduplication, VS Code dark dashboard, doc browser, performance & correctness, GSD-2 StateParser wiring, FastAPI modernization, frontend source rebuild (8 phases, 15 plans, 2026-04-03 → 2026-04-04) — [Archive](milestones/v1.0-ROADMAP.md)
- [x] **v2.0 Feature Pages** — Real drift computation, Drift page, Quick Tasks page, Verification page (2 phases, 4 plans, 2026-04-12) — [Archive](milestones/v2.0-ROADMAP.md)
- [ ] **v3.0 gsd-core Migration** — gsd-core detection & parsing, new document surfacing, progress metrics, enhanced visibility (2 phases)

---

<details>
<summary>v2.0 — Feature Pages (Phases 9-10) — SHIPPED 2026-04-12</summary>

### Phases

- [x] **Phase 9: Drift Computation** - Backend computes real DriftIndicator values from plan age and phase status (completed 2026-04-12)
- [x] **Phase 10: Feature Pages** - Drift, Quick Tasks, and Verification pages wired to live API data (completed 2026-04-12)

### Phase 9: Drift Computation
**Goal**: The backend produces accurate DriftIndicator values for every phase based on plan write time, last updated date, and phase status — replacing the hardcoded DEFERRED placeholder
**Depends on**: Nothing (pure backend change)
**Requirements**: DRFT-01
**Success Criteria** (what must be TRUE):
  1. A phase with no plan file and NOT_STARTED status returns DriftIndicator.DEFERRED
  2. A phase with a plan file last updated more than 30 days ago returns DriftIndicator.MAJOR
  3. A phase with a plan file last updated 7-30 days ago returns DriftIndicator.MINOR
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

</details>

---

## v3.0 — gsd-core Migration

### Phases

- [ ] **Phase 11: gsd-core Support** - Detect, parse, and surface gsd-core projects with all new document types, progress metrics, and GSD-2 removal
- [ ] **Phase 12: Enhanced Visibility** - Requirements traceability, wave visualization, milestone archive browsing, and coverage gap highlighting

---

## Phase Details

### Phase 11: gsd-core Support
**Goal**: Users see gsd-core projects fully rendered in GSD Monitor — correct phase lists, all new document types accessible, progress metrics displayed, pause/resume status visible — while legacy GSD-1 checkbox projects continue working and GSD-2 projects are gone
**Depends on**: Phase 10 (existing parser and discovery infrastructure)
**Requirements**: DETECT-01, DETECT-02, DETECT-03, DETECT-04, DETECT-05, DETECT-06, DOCS-01, DOCS-02, DOCS-03, DOCS-04, DOCS-05, DOCS-06, DOCS-07, DOCS-08, PROG-01, PROG-02, PROG-03
**Success Criteria** (what must be TRUE):
  1. A gsd-core project (with .planning/config.json) appears in the dashboard with its phases parsed from heading-based ROADMAP.md, including milestone-prefixed IDs like "Phase 1-01"
  2. The doc browser for a gsd-core project shows REQUIREMENTS.md, VERIFICATION.md, SUMMARY.md, UI-SPEC.md, UI-REVIEW.md, and config.json alongside existing doc types
  3. A paused gsd-core project displays HANDOFF.json pause status (phase, plan, timestamp) and .continue-here.md resume context in the project view
  4. The project dashboard shows a progress bar or metric widget with completed/total phases and percentage from STATE.md
  5. Legacy GSD-1 checkbox-format projects still render correctly, and no GSD-2 (.gsd/) projects appear
**Plans**: TBD
**UI hint**: yes

### Phase 12: Enhanced Visibility
**Goal**: Users can explore requirements-to-phase mappings, understand plan parallelization, browse shipped milestone history, and spot unmapped requirement gaps — all from within the GSD Monitor UI
**Depends on**: Phase 11 (gsd-core parsing must be in place for data to visualize)
**Requirements**: VIS-01, VIS-02, VIS-03, VIS-04
**Success Criteria** (what must be TRUE):
  1. A requirements traceability table shows each requirement ID mapped to its phase, with unmapped requirements highlighted as gaps
  2. Plan wave assignments are visible, showing which plans within a phase run in parallel groups
  3. User can browse shipped milestones from collapsed archive sections in the ROADMAP, viewing their phases and completion dates
  4. Requirements with no phase coverage are visually distinct (color or icon) so gaps are immediately obvious
**Plans**: TBD
**UI hint**: yes

---

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 9. Drift Computation | 1/1 | Complete | 2026-04-12 |
| 10. Feature Pages | 3/3 | Complete | 2026-04-12 |
| 11. gsd-core Support | 0/0 | Not started | - |
| 12. Enhanced Visibility | 0/0 | Not started | - |
