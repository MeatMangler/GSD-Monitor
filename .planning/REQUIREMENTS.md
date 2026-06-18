# Requirements: GSD Monitor

**Defined:** 2026-06-18
**Core Value:** Developer opens GSD Monitor and immediately understands every project's status with zero duplicate entries and zero confusion

## v3.0 Requirements

Requirements for gsd-core migration. Each maps to roadmap phases.

### Detection & Parsing

- [ ] **DETECT-01**: Monitor detects gsd-core projects via .planning/config.json presence
- [ ] **DETECT-02**: Monitor parses gsd-core ROADMAP.md heading-based phase format (## Phase N: Title with **Goal:** fields)
- [ ] **DETECT-03**: Monitor extracts milestones from ROADMAP.md emoji-marked headings (active, shipped)
- [ ] **DETECT-04**: Monitor supports milestone-prefixed phase IDs (Phase 1-01, Phase 2-03) and displays them as-is
- [ ] **DETECT-05**: Monitor continues to parse legacy GSD-1 checkbox ROADMAP format (- [x] **Phase N: Title**)
- [ ] **DETECT-06**: Monitor no longer discovers or displays GSD-2 (.gsd/) projects

### Document Surfacing

- [ ] **DOCS-01**: Monitor detects and displays REQUIREMENTS.md content for gsd-core projects
- [ ] **DOCS-02**: Monitor detects and displays VERIFICATION.md content per phase
- [ ] **DOCS-03**: Monitor detects and displays per-plan SUMMARY.md content
- [ ] **DOCS-04**: Monitor detects and displays UI-SPEC.md content per phase
- [ ] **DOCS-05**: Monitor detects and displays UI-REVIEW.md content per phase
- [ ] **DOCS-06**: Monitor detects HANDOFF.json and shows pause status (current phase, plan, paused timestamp)
- [ ] **DOCS-07**: Monitor detects .continue-here.md and displays resume context
- [ ] **DOCS-08**: Monitor reads config.json and surfaces workflow mode, model profile, and branching strategy

### Progress & State

- [ ] **PROG-01**: Monitor extracts progress metrics from STATE.md (total_phases, completed_phases, progress_percent)
- [ ] **PROG-02**: Monitor displays progress bar or metric widget on project dashboard
- [ ] **PROG-03**: Monitor parses all three STATE.md syntax variants (bold inline, line-start, pipe-table)

### Enhanced Visibility

- [ ] **VIS-01**: Monitor displays requirements traceability table showing which phases cover which requirements
- [ ] **VIS-02**: Monitor shows plan wave assignments and parallelization grouping
- [ ] **VIS-03**: Monitor can browse shipped milestones from details blocks in ROADMAP.md
- [ ] **VIS-04**: Monitor highlights requirements with no phase coverage (unmapped gaps)

## Validated (v2.0 — shipped)

- [x] **DRFT-01**: Backend computes DriftIndicator from plan_write_time, last_updated, and phase status
- [x] **DRFT-02**: DriftPage displays a per-phase drift table sorted by severity
- [x] **DRFT-03**: Each drift row shows phase number, title, status, drift badge, plan age, last updated
- [x] **DRFT-04**: Drift badges are color-coded (MAJOR=red, MINOR=yellow, NONE=green, DEFERRED=gray)
- [x] **DRFT-05**: Un-started phases collapsed behind toggle
- [x] **QTSK-01**: QuickTasksPage fetches and renders tasks per segment
- [x] **QTSK-02**: Each task row shows title, status badge, dates
- [x] **QTSK-03**: Status badges color-coded
- [x] **QTSK-04**: Empty state when no quick tasks
- [x] **QTSK-05**: Tasks sorted by last_updated descending
- [x] **VERIF-01**: VerificationPage shows per-phase verification summary
- [x] **VERIF-02**: Each row shows has_validation, nyquist_compliant, has_uat badges
- [x] **VERIF-03**: Phase row expands inline validation content as markdown
- [x] **VERIF-04**: Phases without validation dimmed/collapsed with toggle

## Future Requirements

- **DRFT-06**: Git-based drift — compare latest commit date on phase files against plan write date
- **QTSK-06**: Clicking a task navigates to Docs page with that task's PLAN.md pre-selected
- **NOTIF-01**: System notification on phase completion (Windows toast)
- **NOTIF-02**: System notification on verification failure

## Out of Scope

| Feature | Reason |
|---------|--------|
| GSD-2 (.gsd/) support | Deprecated by gsd-core; removing in this milestone |
| Writing to project files | App is read-only by design constraint |
| gsd-core workflow execution | Monitor is a viewer, not a workflow runner |
| Cross-project dependency visualization | High complexity, not core to monitoring value |
| Drift push notifications | DriftPage is pull-only; no background alerting |
| Creating/editing quick tasks from UI | App is read-only |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DETECT-01 | Phase 11 | Pending |
| DETECT-02 | Phase 11 | Pending |
| DETECT-03 | Phase 11 | Pending |
| DETECT-04 | Phase 11 | Pending |
| DETECT-05 | Phase 11 | Pending |
| DETECT-06 | Phase 11 | Pending |
| DOCS-01 | Phase 11 | Pending |
| DOCS-02 | Phase 11 | Pending |
| DOCS-03 | Phase 11 | Pending |
| DOCS-04 | Phase 11 | Pending |
| DOCS-05 | Phase 11 | Pending |
| DOCS-06 | Phase 11 | Pending |
| DOCS-07 | Phase 11 | Pending |
| DOCS-08 | Phase 11 | Pending |
| PROG-01 | Phase 11 | Pending |
| PROG-02 | Phase 11 | Pending |
| PROG-03 | Phase 11 | Pending |
| VIS-01 | Phase 12 | Pending |
| VIS-02 | Phase 12 | Pending |
| VIS-03 | Phase 12 | Pending |
| VIS-04 | Phase 12 | Pending |

**Coverage:**
- v3.0 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0

---
*Requirements defined: 2026-06-18*
*Last updated: 2026-06-18 after roadmap creation*
