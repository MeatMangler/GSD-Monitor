# Summary: Fix Milestone-Based GSD-1 Layout Discovery

status: complete
date: 2026-05-08

## What was done

Fixed `_build_gsd1_segment()` in `gsd_monitor/services/project_discovery.py` with two targeted edits:

1. **Early-return guard** — Before returning `None` when no root ROADMAP.md and no `phases/` dir,
   now checks if `.planning/milestones/` exists and contains any `*-ROADMAP.md` files. If it does,
   the project is a valid milestone-based GSD-1 layout and discovery continues.

2. **Milestone extraction** — In the `else` branch (no root ROADMAP.md parsed), calls
   `RoadmapParser._try_extract_from_milestone_archives()` with a synthetic path so it looks in
   `.planning/milestones/` for `*-ROADMAP.md` files and returns all milestones + phases.

## Result

Projects like SaaS-Dashboard (`.planning/milestones/v1.0-ROADMAP.md`, `v2.0-ROADMAP.md`,
`v2.2-ROADMAP.md`) are now fully discovered:
- All 3 milestones visible (v1.0 / v2.0 / v2.2)
- All 11 phases parsed with correct status
- Phase enrichment follows naturally (finds phase dirs via `_find_archive_phase_dir`,
  loads PLAN files, SUMMARY mtimes, VERIFICATION files, UAT files)

All 33 existing tests pass.
