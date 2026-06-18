# Phase 11: gsd-core Support - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Detect, parse, and surface gsd-core projects with all new document types, progress metrics, and GSD-2 removal. Users see gsd-core projects fully rendered in GSD Monitor -- correct phase lists from heading-based ROADMAP.md, all new document types accessible (REQUIREMENTS, VERIFICATION, SUMMARY, UI-SPEC, UI-REVIEW, HANDOFF, .continue-here, config.json), progress metrics displayed, pause/resume status visible -- while legacy GSD-1 checkbox projects continue working and GSD-2 projects are gone.

</domain>

<decisions>
## Implementation Decisions

### Parser Architecture
- **D-01:** Create a new dedicated `GsdCoreRoadmapParser` class with its own regex for heading-based phases (`## Phase N: Title`), emoji milestone markers, `<details>` archives, and milestone-prefixed phase IDs (`Phase 1-01`). The existing `RoadmapParser` stays untouched for legacy GSD-1 checkbox format.
- **D-02:** Detection strategy uses **config.json presence first** (authoritative, satisfies DETECT-01), with **ROADMAP format sniffing as fallback** for projects that have gsd-core format but no config.json.

### Document Surfacing
- **D-04:** Both approaches for UI: doc browser shows all `.planning/` files naturally (already does), plus add **quick-access shortcuts** for key new doc types AND **small status indicators** (pause badge, config summary) in the project card/header.
- **D-06:** HANDOFF.json shows an **inline summary**: parse phase name, plan name, and paused timestamp, display inline in project view (e.g. "Paused at Phase 5, Plan 2 on Jun 15"). `.continue-here.md` content accessible via doc browser.

### Progress & Pause UI
- **D-08:** Progress bar/metrics appear in **both locations**: compact progress indicator on dashboard project cards (visible at a glance) + fuller metrics in the project detail header (when navigated into a project).

### GSD-2 Removal
- **D-10:** Clean delete of all GSD-2 code in one pass: `Gsd2RoadmapParser`, `_discover_gsd2`, `_enrich_gsd2_project`, `_enrich_gsd2_slice`, `GsdVersion.V2` enum value, `gsd2_repos` tracking in `discover_groups`, and the GSD-2 segment key. No migration path.
- **D-11:** Full frontend cleanup of any GSD-2 version checks, V2-specific rendering, or gsd2 segment handling.

### Claude's Discretion
- **D-03:** Milestone-prefixed phase ID handling (e.g. `Phase 1-01`) -- how to store and display in PhaseEntry model and frontend. Choose based on existing model structure and frontend needs.
- **D-05:** Backend model representation for new doc types -- boolean flags (consistent with existing `has_context`/`has_research`/`has_plan` pattern) vs doc inventory list. Follow existing conventions.
- **D-07:** config.json surfacing level -- determine right balance between summary badges and full JSON view.
- **D-09:** STATE.md parsing strategy for 3 syntax variants (bold inline, line-start, pipe-table) plus YAML frontmatter. Choose optimal parsing approach.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Roadmap
- `.planning/REQUIREMENTS.md` -- All 17 requirements for this phase (DETECT-01 through DETECT-06, DOCS-01 through DOCS-08, PROG-01 through PROG-03)
- `.planning/ROADMAP.md` -- Phase 11 success criteria (5 criteria) and dependency on Phase 10

### Existing Parsers (to understand patterns)
- `gsd_monitor/parsers/roadmap.py` -- `RoadmapParser` (GSD-1 checkbox format, must continue working)
- `gsd_monitor/parsers/gsd2_roadmap.py` -- `Gsd2RoadmapParser` (to be removed)
- `gsd_monitor/parsers/state_parser.py` -- `StateParser` (needs progress metric extraction)
- `gsd_monitor/parsers/plan_parser.py` -- `PlanParser` (existing pattern for new parsers)

### Discovery & Models
- `gsd_monitor/services/project_discovery.py` -- `ProjectDiscoveryService`, `_enrich_phase`, `_discover_gsd2` (GSD-2 code to remove), `_compute_drift`
- `gsd_monitor/models/core.py` -- `PhaseEntry`, `GsdProject`, `Milestone`, `StateInfo` (models to extend)
- `gsd_monitor/models/enums.py` -- `GsdVersion`, `PhaseStatus`, `MilestoneStatus` (V2 enum to remove)

### API & Frontend
- `gsd_monitor/api/app.py` -- API endpoints (may need new endpoints or response fields)
- `frontend/src/api.ts` -- TypeScript interfaces (`PhasePayload`, `GsdProjectPayload`, `MilestonePayload`)

### Prior Phase Context
- `.planning/phases/09-drift-computation/09-CONTEXT.md` -- Drift computation decisions (D-01 through D-05) that apply to enrichment changes

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `RoadmapParser._try_extract_from_milestone_archives()` -- pattern for handling archived milestones, relevant for gsd-core `<details>` archive parsing
- `_enrich_phase()` -- already detects CONTEXT, RESEARCH, VALIDATION, UAT, SUMMARY, PLAN files; extend for new doc types
- `_compute_drift()` -- drift computation helper, already wired into both GSD-1 and GSD-2 enrichment; will simplify to GSD-1/gsd-core only
- `_strip_frontmatter()` and `_try_read()` -- utility functions for safe file reading
- Existing `has_*` boolean flag pattern on `PhaseEntry` -- consistent pattern for new doc type flags

### Established Patterns
- Parser classes are static with `parse(file_path: str) -> ParseResult` interface
- `ParseResult.ok(value)` / `ParseResult.err(msg)` for all parser returns
- Discovery scans `.planning` dirs, builds `SegmentModel`, enriches via `_enrich_planning`
- Frontend mirrors backend models 1:1 via TypeScript interfaces in `api.ts`
- Dark theme with `bg-zinc-950`, `text-zinc-100/400/500` color scale

### Integration Points
- `_build_gsd1_segment()` -- where gsd-core detection fork will go (check config.json, choose parser)
- `discover_groups()` -- GSD-2 scanning loop to remove
- Frontend `DashboardPage.tsx` -- where progress indicators will be added to project cards
- Frontend `ShellLayout.tsx` -- project detail header where fuller metrics go
- Doc browser quick-access list -- where new doc type shortcuts will be added

</code_context>

<specifics>
## Specific Ideas

No specific requirements -- open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 11-gsd-core Support*
*Context gathered: 2026-06-18*
