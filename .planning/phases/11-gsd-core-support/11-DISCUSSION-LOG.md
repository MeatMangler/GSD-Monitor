# Phase 11: gsd-core Support - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md -- this log preserves the alternatives considered.

**Date:** 2026-06-18
**Phase:** 11-gsd-core Support
**Areas discussed:** Parser architecture, Document surfacing, Progress & pause UI, GSD-2 removal scope

---

## Parser Architecture

### Q1: How should we handle the gsd-core ROADMAP format alongside legacy GSD-1?

| Option | Description | Selected |
|--------|-------------|----------|
| New parser class | Create a dedicated GsdCoreRoadmapParser with its own regex. RoadmapParser stays untouched for legacy GSD-1. Discovery checks config.json first to pick which parser to use. | Yes |
| Extend RoadmapParser | Add gsd-core parsing as a fallback branch inside the existing RoadmapParser. | |
| You decide | Let Claude pick the best approach based on codebase conventions. | |

**User's choice:** New parser class (Recommended)

### Q2: How should discovery decide which parser to use?

| Option | Description | Selected |
|--------|-------------|----------|
| config.json presence | If .planning/config.json exists, use gsd-core parser. Otherwise, legacy GSD-1. | |
| ROADMAP format sniffing | Read first few lines and detect heading-based vs checkbox format. | |
| Both with priority | Check config.json first (authoritative). If absent, sniff ROADMAP.md format as fallback. | Yes |

**User's choice:** Both with priority

### Q3: Milestone-prefixed phase IDs (Phase 1-01) numbering?

| Option | Description | Selected |
|--------|-------------|----------|
| Store as-is with string ID | Add phase_id: str field, keep number: int for sorting. | |
| Split into milestone + number | Parse into milestone_number and phase_number. | |
| You decide | Let Claude pick based on existing model. | Yes |

**User's choice:** You decide

---

## Document Surfacing

### Q1: How should the 8 new document types appear in the UI?

| Option | Description | Selected |
|--------|-------------|----------|
| Expand doc browser | New doc types naturally appear in existing doc browser. Add curated quick-access entries. | |
| Dedicated sections | Add new sections/panels in the project detail view for each doc category. | |
| Both approaches | Doc browser shows everything, plus quick-access shortcuts AND small status indicators in project card/header. | Yes |

**User's choice:** Both approaches

### Q2: Backend model representation for new doc types?

| Option | Description | Selected |
|--------|-------------|----------|
| Boolean flags on PhaseEntry | Add has_ui_spec, has_ui_review, etc. Consistent with existing pattern. | |
| Doc inventory list | Add doc_types: list[str] field. More flexible, fewer fields. | |
| You decide | Let Claude pick based on existing model conventions. | Yes |

**User's choice:** You decide

### Q3: HANDOFF.json and .continue-here.md detail level?

| Option | Description | Selected |
|--------|-------------|----------|
| Status badge only | Show a 'Paused' badge. Clicking opens doc browser. | |
| Inline summary | Parse HANDOFF.json to extract phase, plan, timestamp. Show inline. | Yes |
| Rich pause card | Dedicated card with parsed HANDOFF fields AND .continue-here.md rendered as markdown. | |

**User's choice:** Inline summary

### Q4: config.json surfacing level?

| Option | Description | Selected |
|--------|-------------|----------|
| Key fields summary | Extract workflow mode, model profile, branching strategy as labels/badges. | |
| Full config view | Full JSON in doc browser plus summary badges. | |
| You decide | Let Claude determine the right level of detail. | Yes |

**User's choice:** You decide

---

## Progress & Pause UI

### Q1: Where should progress bar/metrics appear?

| Option | Description | Selected |
|--------|-------------|----------|
| Dashboard project card | Progress bar directly on each project's card in the dashboard list. | |
| Project detail header | Show progress in the header when selecting a project. | |
| Both locations | Compact indicator on dashboard cards + fuller metrics in project detail header. | Yes |

**User's choice:** Both locations

### Q2: STATE.md parsing for 3 syntax variants?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend StateParser | Add all 3 variant patterns to existing StateParser class. | |
| YAML frontmatter priority | Parse frontmatter first, fall back to body-text regex for 3 variants. | |
| You decide | Let Claude determine the best parsing strategy. | Yes |

**User's choice:** You decide

---

## GSD-2 Removal Scope

### Q1: How should GSD-2 code be removed?

| Option | Description | Selected |
|--------|-------------|----------|
| Clean delete | Remove all GSD-2 code in one pass. No migration path. | Yes |
| Keep enum, remove code | Remove logic but keep GsdVersion.V2 for backwards compatibility. | |
| You decide | Let Claude determine cleanest removal approach. | |

**User's choice:** Clean delete (Recommended)

### Q2: Frontend GSD-2 cleanup?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, full cleanup | Remove any GSD-2 version checks, V2-specific rendering, or gsd2 segment handling. | Yes |
| You decide | Let Claude determine what to remove. | |

**User's choice:** Yes, full cleanup

---

## Claude's Discretion

- D-03: Milestone-prefixed phase ID storage/display approach
- D-05: Backend model representation for new doc types (boolean flags vs doc inventory)
- D-07: config.json surfacing level
- D-09: STATE.md parsing strategy for 3 syntax variants + YAML frontmatter

## Deferred Ideas

None -- discussion stayed within phase scope.
