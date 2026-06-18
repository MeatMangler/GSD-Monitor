# Phase 12: Enhanced Visibility - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can explore requirements-to-phase mappings, understand plan parallelization, browse shipped milestone history, and spot unmapped requirement gaps — all from within the GSD Monitor UI. This is a new "Insights" page with three tabs: Requirements, Waves, and Archives.

</domain>

<decisions>
## Implementation Decisions

### Page Structure
- **D-01:** Single new page with three tabs (Requirements, Waves, Archives) instead of multiple separate pages. Keeps nav bar clean — already have 6 nav items.
- **D-02:** Tab switching uses local React `useState` — no URL hash fragments. Desktop app doesn't need deep-linking.

### Requirements Traceability (VIS-01, VIS-04)
- **D-03:** Requirements-first table layout — rows are requirements (VIS-01, DETECT-01...), columns show phase mapping and status. Natural reading order for "which reqs are covered?"
- **D-04:** Unmapped requirement gaps highlighted with color-coded rows (red/amber background tint), matching existing badge color patterns.
- **D-05:** Data sourced by parsing the `## Traceability` table from REQUIREMENTS.md. New parser extracts requirement-to-phase mappings as structured data.
- **D-06:** Requirements grouped by category (Detection, Documents, Progress, Visibility) with section headers, matching the `###` headings in REQUIREMENTS.md.

### Wave Visualization (VIS-02)
- **D-07:** Wave table grouped by phase, showing plan names with wave numbers. Plans in the same wave displayed together (e.g., "Wave 2: Plan 02 | Plan 03").
- **D-08:** Only multi-wave phases shown — single-wave phases filtered out since parallelization is the interesting case.
- **D-09:** Wave data extracted from PLAN.md YAML frontmatter (`wave: N`) via existing PlanParser. Surfaced through PhaseEntry to frontend.

### Milestone Archive Browsing (VIS-03)
- **D-10:** Collapsed accordion of shipped milestones — each shows title, completion date, and phase count. Expand to see phase list with status.
- **D-11:** Archives tab shows shipped milestones only — active milestone already visible on Dashboard.

### Claude's Discretion
- **D-12:** Nav label for the new page — choose what fits the existing nav style (e.g., "Insights", "Traceability", or another label).
- **D-13:** Backend API design — whether to add new endpoints or extend existing `/api/groups` response with traceability and wave data. Follow path of least resistance.
- **D-14:** Exact tab styling and component structure — follow existing page patterns (DriftPage, VerificationPage).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Roadmap
- `.planning/REQUIREMENTS.md` — VIS-01 through VIS-04 requirements; `## Traceability` table is the data source for requirements mapping
- `.planning/ROADMAP.md` — Phase 12 success criteria (4 criteria) and dependency on Phase 11

### Existing Parsers (patterns to follow)
- `gsd_monitor/parsers/gsd_core_roadmap.py` — `GsdCoreRoadmapParser._extract_archived_milestones()` already parses archived milestones from `<details>` blocks
- `gsd_monitor/parsers/plan_parser.py` — `PlanParser` reads PLAN.md frontmatter; extend for `wave` field extraction
- `gsd_monitor/parsers/roadmap.py` — `RoadmapParser._try_extract_from_milestone_archives()` handles legacy milestone archive parsing

### Models & Discovery
- `gsd_monitor/models/core.py` — `PhaseEntry` (has `is_archived`, `archive_milestone`, `has_requirements`), `Milestone`, `GsdProject`
- `gsd_monitor/services/project_discovery.py` — `_enrich_phase()`, `_find_archive_phase_dir()` for archive handling

### Frontend Pages (pattern reference)
- `frontend/src/pages/DriftPage.tsx` — Table-based feature page with color-coded badges and collapsible sections
- `frontend/src/pages/VerificationPage.tsx` — Expandable rows with inline content, collapsible unvalidated section
- `frontend/src/api.ts` — TypeScript interfaces (`PhasePayload`, `MilestonePayload`) to extend

### Prior Phase Context
- `.planning/phases/11-gsd-core-support/11-CONTEXT.md` — Phase 11 decisions on document surfacing, progress UI, parser architecture

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GsdCoreRoadmapParser._extract_archived_milestones()` — already parses `<details>` archive blocks into `Milestone` objects with `SHIPPED` status; data already flows through API
- `_enrich_phase()` — detects PLAN files and reads frontmatter; extend for wave extraction
- `PhaseEntry.is_archived`, `archive_milestone` — existing archive fields on phase model
- `MilestonePayload` — TypeScript interface already has `status`, `phases`, `code`, `vision` fields
- DriftPage/VerificationPage — established patterns for table-based feature pages with color-coded badges

### Established Patterns
- Feature pages: `{Feature}Page.tsx` in `src/pages/`, named exports, data from `useApp()` context
- Dark theme: `bg-zinc-950`, `text-zinc-100/400/500` color scale
- Color badges: red (major/gap), yellow (minor), green (complete/none), gray (deferred)
- Parser pattern: static `parse(file_path: str) -> ParseResult` with `ParseResult.ok(value)` / `ParseResult.err(msg)`
- Frontend mirrors backend 1:1 via TypeScript interfaces in `api.ts`

### Integration Points
- `ShellLayout.tsx` — nav bar where new page link is added
- `frontend/src/main.tsx` — React Router where new route is registered
- `frontend/src/api.ts` — where new TypeScript interfaces for traceability/wave data are added
- `gsd_monitor/api/app.py` — where new API endpoints are registered (if needed)
- `PLAN.md` frontmatter `wave: N` field — already present in all existing plans

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 12-Enhanced Visibility*
*Context gathered: 2026-06-18*
