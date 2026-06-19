---
status: complete
phase: 11-gsd-core-support
source: 11-01-SUMMARY.md, 11-02-SUMMARY.md
started: 2026-06-18T00:00:00Z
updated: 2026-06-18T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. gsd-core Project Detection
expected: A project with a `.planning/config.json` file is detected as `gsd-core` version. The API response shows `version: "gsd-core"` for that project. Projects without config.json but with `## Phase N` headings in ROADMAP.md also detect as gsd-core.
result: pass

### 2. GSD-2 Projects No Longer Appear
expected: Projects that only have a `.gsd/` directory (no `.planning/`) do not appear in the project list. The app no longer scans for or displays GSD-2 projects.
result: pass

### 3. Version Badge Display
expected: On the Dashboard, gsd-core projects show a blue-tinted "gsd-core" badge. GSD-1 projects show a muted gray "gsd1" badge. No "gsd2" badge exists anywhere.
result: pass

### 4. Progress Bar — Compact (Stats Card)
expected: The Completion stats card shows a thin (4px) green progress bar fill representing phase completion percentage. Only visible when the project has progress data from STATE.md.
result: pass

### 5. Progress Bar — Detail
expected: Below the stats grid, an 8px progress bar appears with a label like "X of Y phases complete N%". Only visible when the project has progress data.
result: pass

### 6. Pause Banner
expected: When a project has a HANDOFF.json file (indicating paused work), an amber-themed banner appears between the breadcrumb and stats grid showing "Paused" with phase/plan info and the paused timestamp.
result: pass

### 7. Config Badge Row
expected: When a project has a config.json with workflow settings, small gray badges appear below the version badge showing workflow_mode, model_profile, and/or branching_strategy values.
result: pass

### 8. Milestone-Prefixed Phase IDs
expected: For gsd-core projects with milestone-prefixed phases (e.g. Phase 1-01), the phase list buttons and drawer title display the code "1-01" instead of just "01".
result: pass

### 9. DocsPage Quick-Access Shortcuts
expected: On the Docs page, when the in-progress phase has UI-SPEC, UI-REVIEW, VERIFICATION, or SUMMARY files, corresponding quick-access shortcut buttons appear (e.g. "UI-SPEC (11)", "SUMMARY (11)") that navigate to those documents.
result: pass

### 10. State Parser Progress Extraction
expected: Projects with STATE.md containing progress data (YAML frontmatter, bold inline, or pipe-table format) show accurate completed_phases, total_phases, and progress_percent values reflected in the progress bars.
result: pass

## Summary

total: 10
passed: 10
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
