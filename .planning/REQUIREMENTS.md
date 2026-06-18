# Requirements: GSD Monitor

**Defined:** 2026-06-18
**Core Value:** Developer opens GSD Monitor and immediately understands every project's status with zero duplicate entries and zero confusion

## v3.0 Requirements

Requirements for gsd-core migration. Each maps to roadmap phases.

### Detection & Parsing

- [x] **DETECT-01**: Monitor detects gsd-core projects via .planning/config.json presence
- [x] **DETECT-02**: Monitor parses gsd-core ROADMAP.md heading-based phase format (## Phase N: Title with **Goal:** fields)
- [x] **DETECT-03**: Monitor extracts milestones from ROADMAP.md emoji-marked headings (active, shipped)
- [x] **DETECT-04**: Monitor supports milestone-prefixed phase IDs (Phase 1-01, Phase 2-03) and displays them as-is
- [x] **DETECT-05**: Monitor continues to parse legacy GSD-1 checkbox ROADMAP format (- [x] **Phase N: Title**)
- [x] **DETECT-06**: Monitor no longer discovers or displays GSD-2 (.gsd/) projects

### Document Surfacing

- [x] **DOCS-01**: Monitor detects and displays REQUIREMENTS.md content for gsd-core projects
- [x] **DOCS-02**: Monitor detects and displays VERIFICATION.md content per phase
- [x] **DOCS-03**: Monitor detects and displays per-plan SUMMARY.md content
- [x] **DOCS-04**: Monitor detects and displays UI-SPEC.md content per phase
- [x] **DOCS-05**: Monitor detects and displays UI-REVIEW.md content per phase
- [x] **DOCS-06**: Monitor detects HANDOFF.json and shows pause status (current phase, plan, paused timestamp)
- [x] **DOCS-07**: Monitor detects .continue-here.md and displays resume context
- [x] **DOCS-08**: Monitor reads config.json and surfaces workflow mode, model profile, and branching strategy

### Progress & State

- [x] **PROG-01**: Monitor extracts progress metrics from STATE.md (total_phases, completed_phases, progress_percent)
- [x] **PROG-02**: Monitor displays progress bar or metric widget on project dashboard
- [x] **PROG-03**: Monitor parses all three STATE.md syntax variants (bold inline, line-start, pipe-table)

### Enhanced Visibility

- [x] **VIS-01**: Monitor displays requirements traceability table showing which phases cover which requirements
- [x] **VIS-02**: Monitor shows plan wave assignments and parallelization grouping
- [x] **VIS-03**: Monitor can browse shipped milestones from details blocks in ROADMAP.md
- [x] **VIS-04**: Monitor highlights requirements with no phase coverage (unmapped gaps)

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
| DETECT-01 | Phase 11 | Complete |
| DETECT-02 | Phase 11 | Complete |
| DETECT-03 | Phase 11 | Complete |
| DETECT-04 | Phase 11 | Complete |
| DETECT-05 | Phase 11 | Complete |
| DETECT-06 | Phase 11 | Complete |
| DOCS-01 | Phase 11 | Complete |
| DOCS-02 | Phase 11 | Complete |
| DOCS-03 | Phase 11 | Complete |
| DOCS-04 | Phase 11 | Complete |
| DOCS-05 | Phase 11 | Complete |
| DOCS-06 | Phase 11 | Complete |
| DOCS-07 | Phase 11 | Complete |
| DOCS-08 | Phase 11 | Complete |
| PROG-01 | Phase 11 | Complete |
| PROG-02 | Phase 11 | Complete |
| PROG-03 | Phase 11 | Complete |
| VIS-01 | Phase 12 | Complete |
| VIS-02 | Phase 12 | Complete |
| VIS-03 | Phase 12 | Complete |
| VIS-04 | Phase 12 | Complete |

**Coverage:**

- v3.0 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0

---
*Requirements defined: 2026-06-18*
*Last updated: 2026-06-18 after roadmap creation*
