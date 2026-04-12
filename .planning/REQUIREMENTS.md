# Requirements: GSD Monitor v2.0

## Milestone Goal

Surface the three stub pages — Drift, Quick Tasks, and Verification — with real data from the already-built backend.

---

## Active Requirements

### Drift Detection

- [x] **DRFT-01**: Backend computes `DriftIndicator` from `plan_write_time`, `last_updated`, and phase `status` — replacing the hardcoded `DEFERRED` placeholder in `_enrich_phase` and `_enrich_gsd2_slice`
  - NONE: no plan, or phase complete with recent last_updated (≤30 days)
  - MINOR: has plan, last_updated is 7–30 days old (or plan written but no summary yet and < 14 days)
  - MAJOR: has plan, no summary and plan > 14 days old, or last_updated > 30 days old on active phase
  - DEFERRED: phase intentionally parked (status NOT_STARTED with no plan) — keep as fallback
- [x] **DRFT-02**: `DriftPage` displays a per-phase drift table for the active project, sorted by drift severity (MAJOR first, then MINOR, then NONE/DEFERRED)
- [x] **DRFT-03**: Each drift row shows: phase number, title, current status, drift level badge, plan age (days since `plan_write_time`), and last updated date
- [x] **DRFT-04**: Drift badges are color-coded — MAJOR=red, MINOR=yellow, NONE=muted green, DEFERRED=gray
- [x] **DRFT-05**: Phases with no plan and NOT_STARTED status are collapsed/hidden by default with a "Show N un-started" toggle

### Quick Tasks

- [ ] **QTSK-01**: `QuickTasksPage` fetches from the existing `/api/quick-tasks/{planningPath}` endpoint and renders the task list for the active segment
- [ ] **QTSK-02**: Each task row shows: title, status badge, created date, last updated date
- [ ] **QTSK-03**: Status badges are color-coded — open=gray, in_progress=yellow, complete=green
- [ ] **QTSK-04**: Empty state is shown when no quick tasks exist for the active project (not an error)
- [ ] **QTSK-05**: Tasks are sorted by last_updated descending (most recently active first)

### Verification

- [x] **VERIF-01**: `VerificationPage` shows a per-phase verification summary for the active project
- [x] **VERIF-02**: Each row shows: phase number, title, `has_validation` badge, `nyquist_compliant` status (pass/fail/unknown), and `has_uat` badge
- [x] **VERIF-03**: Selecting a phase row expands inline to show `validation_content` rendered as markdown
- [x] **VERIF-04**: Phases without any validation file (`has_validation=false`) are shown in a dimmed/collapsed section with a toggle to reveal them

---

## Future Requirements (Deferred)

- **DRFT-06**: Git-based drift — compare latest commit date on phase files against plan write date (needs `GitService.get_latest_file_commit_date()`)
- **QTSK-06**: Clicking a task navigates to the Docs page with that task's PLAN.md pre-selected (requires shared routing state or URL param on DocsPage)
- **NOTIF-01**: System notification on phase completion (Windows toast)
- **NOTIF-02**: System notification on verification failure

---

## Out of Scope

- **Drift push notifications** — DriftPage is pull-only (load on visit); no background alerting in v2
- **Creating or editing quick tasks from the UI** — app is read-only
- **UAT detail page** — `has_uat` badge shown on Verification page but no dedicated UAT viewer in v2

---

## Traceability

| Requirement | Phase |
|-------------|-------|
| DRFT-01     | 9     |
| DRFT-02     | 10    |
| DRFT-03     | 10    |
| DRFT-04     | 10    |
| DRFT-05     | 10    |
| QTSK-01     | 10    |
| QTSK-02     | 10    |
| QTSK-03     | 10    |
| QTSK-04     | 10    |
| QTSK-05     | 10    |
| VERIF-01    | 10    |
| VERIF-02    | 10    |
| VERIF-03    | 10    |
| VERIF-04    | 10    |
