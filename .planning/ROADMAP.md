# Roadmap: GSD Monitor

## Milestones

- [x] **v1.0** — Worktree deduplication, VS Code dark dashboard, doc browser, performance & correctness (8 phases, 15 plans, 2026-04-04) — [Archive](milestones/v1.0-ROADMAP.md)
- [x] **v2.0 Feature Pages** — Drift computation, Drift/Quick Tasks/Verification pages (2 phases, 4 plans, 2026-04-12) — [Archive](milestones/v2.0-ROADMAP.md)
- [x] **v3.0 gsd-core Migration** — gsd-core detection & parsing, document surfacing, progress metrics, enhanced visibility (2 phases, 4 plans, 2026-06-18) — [Archive](milestones/v3.0-ROADMAP.md)

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

- [ ] Phase 13: Installation Script — PowerShell guided installer; clone, venv, frontend build, .bat launcher, desktop shortcut, WebView2 check

## Phase Details

### Phase 13: Installation Script

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
| 13. Installation Script | v4.0 | 0/? | Pending | — |
