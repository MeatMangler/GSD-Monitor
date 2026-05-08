# Fix: Milestone-Based GSD-1 Layout Discovery

## Problem

GSD-1 projects that store all planning under `.planning/milestones/` (no root ROADMAP.md,
no `phases/` dir) are completely invisible to GSD Monitor.

Root cause: `_build_gsd1_segment()` in `project_discovery.py` returns `None` when both
`.planning/ROADMAP.md` and `.planning/phases/` are absent — even though
`.planning/milestones/*-ROADMAP.md` files exist and `_try_extract_from_milestone_archives()`
already knows how to parse them.

## Fix

In `project_discovery.py → _build_gsd1_segment()`:

1. Before returning `None`, check if `.planning/milestones/` exists and contains `*-ROADMAP.md` files.
2. If yes, call `RoadmapParser._try_extract_from_milestone_archives()` directly to extract
   milestone+phase data, then continue with normal enrichment.

## Files Changed

- `gsd_monitor/services/project_discovery.py` — two targeted edits to `_build_gsd1_segment`
