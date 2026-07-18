# Roadmap: GSD Monitor

## Milestones

- [x] **v1.0** — Worktree deduplication, VS Code dark dashboard, doc browser, performance & correctness (8 phases, 15 plans, 2026-04-04) — [Archive](milestones/v1.0-ROADMAP.md)
- [x] **v2.0 Feature Pages** — Drift computation, Drift/Quick Tasks/Verification pages (2 phases, 4 plans, 2026-04-12) — [Archive](milestones/v2.0-ROADMAP.md)
- [x] **v3.0 gsd-core Migration** — gsd-core detection & parsing, document surfacing, progress metrics, enhanced visibility (2 phases, 4 plans, 2026-06-18) — [Archive](milestones/v3.0-ROADMAP.md)
- [x] **v4.0 gsd-core Full Visibility** — P0 correctness fixes, P1 artifact visibility, P2 surface depth (3 phases, 10 plans, 2026-07-18)

## Phases

<details>
<summary>v1.0 (Phases 1-8) — SHIPPED 2026-04-04</summary>

- [x] Phase 1: Worktree Deduplication — completed 2026-04-03
- [x] Phase 2: Visual Redesign — completed 2026-04-03
- [x] Phase 3: Doc Browser — completed 2026-04-03
- [x] Phase 4: Performance & Correctness — completed 2026-04-03
- [x] Phase 5: GSD-2 StateParser Wiring — completed 2026-04-03
- [x] Phase 6: Tech Debt Remediation — completed 2026-04-04
- [x] Phase 7: Frontend Source Completion — completed 2026-04-04
- [x] Phase 8: Phase 01 Verification Cleanup — completed 2026-04-04

</details>

<details>
<summary>v2.0 Feature Pages (Phases 9-10) — SHIPPED 2026-04-12</summary>

- [x] Phase 9: Drift Computation (1/1 plans) — completed 2026-04-12
- [x] Phase 10: Feature Pages (3/3 plans) — completed 2026-04-12

</details>

<details>
<summary>v3.0 gsd-core Migration (Phases 11-12) — SHIPPED 2026-06-18</summary>

- [x] Phase 11: gsd-core Support (2/2 plans) — completed 2026-06-18
- [x] Phase 12: Enhanced Visibility (2/2 plans) — completed 2026-06-18

</details>

## Active

- [ ] Phase 14: gsd-core P0 Correctness Bug Fixes — unprefixed artifact fallback, phase-dir enrichment collision fix, XML task parsing, RequirementsParser wiring
- [x] Phase 15: gsd-core P1 Artifact Visibility — Decision parser, code review findings, package legitimacy audit (completed 2026-07-18)
- [x] Phase 16: gsd-core P2 Surface Depth — backlog phases, config signals, PROJECT.md vision, VerificationPage structured render, artifact explorers (completed 2026-07-18)

## Deferred

- [ ] Phase 13: Installation Script — PowerShell guided installer; clone, venv, frontend build, .bat launcher, desktop shortcut, WebView2 check (deferred to v5.0)

## Phase Details

### Phase 14: gsd-core P0 Correctness Bug Fixes

**Goal**: Every gsd-core phase artifact (CONTEXT.md, RESEARCH.md, VERIFICATION.md, UAT.md) is found correctly; phases in multi-phase milestones each enrich from their own directory; XML plan tasks parse into the todo list; reserved dirs and RequirementsParser wiring are hardened
**Depends on**: Phase 12
**Requirements**: VIS-P0-01, VIS-P0-02, VIS-P0-03, VIS-P0-04
**Success Criteria** (what must be TRUE):

  1. A gsd-core phase directory containing bare `CONTEXT.md`, `RESEARCH.md`, `VERIFICATION.md`, `UAT.md` (no prefix) sets `has_context`, `has_research`, `has_validation`, `has_uat` to `true` and populates content fields
  2. A milestone with phases `1-01`, `1-02`, `1-03` each enrich from their own `01-01-*`, `01-02-*`, `01-03-*` directories — no collision
  3. A gsd-core `XX-YY-PLAN.md` containing `<task>` XML blocks produces a non-empty `todos` list on the phase
  4. Directories `spikes`, `sketches`, `reports`, `todos`, `debug`, `intel` are in `RESERVED` and not walked as fake projects
  5. `RequirementsParser` is confirmed called from the discovery pipeline; requirements appear in API responses for projects that have `REQUIREMENTS.md`

**Plans:** 3/3 plans complete
Plans:

- [x] 14-01-PLAN.md — Unprefixed artifact fallback: `_resolve_artifact` helper trying `{padded}-NAME.md` then bare `NAME.md`; fix CONTEXT, RESEARCH, VERIFICATION, UAT; add tests
- [x] 14-02-PLAN.md — Phase-dir enrichment collision fix: `_phase_dir_prefix(phase)` helper that uses full padded code (`1-01` → `01-01-`) for milestone-prefixed phases; add collision regression tests
- [x] 14-03-PLAN.md — XML task parsing in `PlanParser` (`<task>` blocks → `TodoItem`); `RequirementsParser` wiring audit + export from `__init__.py`; reserved dir hardening

### Phase 15: gsd-core P1 Artifact Visibility

**Goal**: High-value gsd-core artifacts — decisions, code review findings, package legitimacy audit — are parsed and surfaced as badges and content in the Dashboard and Verification pages
**Depends on**: Phase 14
**Requirements**: VIS-P1-01, VIS-P1-02, VIS-P1-03
**Success Criteria** (what must be TRUE):

  1. A phase with a CONTEXT.md containing `- **D-01:** ...` blocks shows decisions in the phase drawer with covered/uncovered indicator
  2. A phase with an `XX-REVIEW.md` shows a severity badge (Critical/Warning/Info counts) in the phase list and an expanded section in VerificationPage
  3. A phase with a RESEARCH.md Package Legitimacy Audit table shows flagged/suspicious packages as a security signal

**Plans:** 3/3 plans complete
Plans:

- [x] 15-01-PLAN.md — `DecisionParser` + `PhaseEntry.decisions` field + Dashboard phase drawer integration with coverage indicator
- [x] 15-02-PLAN.md — `ReviewParser` (XX-REVIEW.md severity counts) + phase badge on Dashboard + section in VerificationPage
- [x] 15-03-PLAN.md — Package legitimacy audit parser (RESEARCH.md `## Package Legitimacy Audit`) + security signal display per phase

### Phase 16: gsd-core P2 Surface Depth

**Goal**: Backlog phases, full config visibility, PROJECT.md vision, structured verification render, and top-level gsd-core artifact explorers (Spikes, Threads, Codebase/Intel) are surfaced in the UI
**Depends on**: Phase 15
**Requirements**: VIS-P2-01, VIS-P2-02, VIS-P2-03, VIS-P2-04
**Success Criteria** (what must be TRUE):

  1. `999.x`-numbered backlog phases appear in the roadmap and are enriched from matching directories
  2. Dashboard shows `nyquist_validation`, `discuss_mode`, `ui_phase` config badges; PROJECT.md vision appears as a callout
  3. VerificationPage renders gsd-core VERIFICATION.md with structured sections (open blockers highlighted separately from passing gates)
  4. A new Artifacts page (or sidebar section) lists Spikes, Threads, Codebase docs with read-only detail views; Sketches open externally via existing open API

**Plans:** 4/4 plans complete
Plans:

- [x] 16-01-PLAN.md — Backlog phases (999.x): fix `_HEADING_PHASE` regex for dot separator + `_enrich_phase` dir matching
- [x] 16-02-PLAN.md — Config signal expansion (nyquist_validation, discuss_mode, ui_phase) + PROJECT.md vision callout on Dashboard
- [x] 16-03-PLAN.md — VerificationPage structured render: parse VERIFICATION.md sections, highlight open blockers vs passing gates
- [x] 16-04-PLAN.md — Top-level artifact explorers: new API endpoints for Spikes/Threads/Codebase/Intel + frontend views

### Phase 13: Installation Script (deferred to v5.0)

**Goal**: A developer or power user runs a single PowerShell script and ends up with GSD Monitor fully installed — repo cloned, virtualenv created, frontend built, a `.bat` launcher in place, a desktop shortcut created, and WebView2 presence verified
**Depends on**: Phase 12
**Requirements**: INST-01
**Success Criteria** (what must be TRUE):

  1. Running the installer script on a clean Windows machine with Git, Python 3.11+, and Node.js results in a working GSD Monitor launch via the created shortcut
  2. The script checks for WebView2 and prints a clear message (with download link) if it is absent
  3. If any prerequisite (Git, Python, Node) is missing, the script exits with a human-readable error naming the missing tool
  4. Running the installer a second time on an already-installed location does not corrupt the existing installation

**Plans:** 0/1 plans complete
Plans:

- [ ] 13-01-PLAN.md — PowerShell installer: prereq checks, clone, venv, frontend build, launcher, shortcut, upgrade flow

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-8 | v1.0 | 15/15 | Complete | 2026-04-04 |
| 9. Drift Computation | v2.0 | 1/1 | Complete | 2026-04-12 |
| 10. Feature Pages | v2.0 | 3/3 | Complete | 2026-04-12 |
| 11. gsd-core Support | v3.0 | 2/2 | Complete | 2026-06-18 |
| 12. Enhanced Visibility | v3.0 | 2/2 | Complete | 2026-06-18 |
| 14. gsd-core P0 Correctness | v4.0 | 3/3 | Complete | 2026-07-18 |
| 15. gsd-core P1 Visibility | v4.0 | 3/3 | Complete   | 2026-07-18 |
| 16. gsd-core P2 Depth | v4.0 | 4/4 | Complete   | 2026-07-18 |
| 13. Installation Script | v5.0 | 0/1 | Deferred | — |
