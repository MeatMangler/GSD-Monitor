# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v3.0 — gsd-core Migration

**Shipped:** 2026-06-18
**Phases:** 2 | **Plans:** 4 | **Tasks:** 10

### What Was Built
- GsdCoreRoadmapParser for heading-based ROADMAP.md with emoji milestones, milestone-prefixed IDs, archived details blocks
- 8 new document types surfaced (REQUIREMENTS, VERIFICATION, SUMMARY, UI-SPEC, UI-REVIEW, HANDOFF, .continue-here, config.json)
- Complete GSD-2 (.gsd/) code removal from discovery, parsers, models, and tests
- StateParser progress extraction from 3 syntax variants with dashboard progress bars
- InsightsPage with Requirements traceability (gap highlighting), Waves visualization, and Archives browsing
- Resume context banner for .continue-here.md on dashboard

### What Worked
- **Two-phase structure** (Make it Work + Enhanced Visibility) cleanly separated backend parsing from frontend visualization
- **Wave-based parallelization** — backend Wave 1 completed before frontend Wave 2, avoiding integration conflicts
- **Static parser pattern** (GsdCoreRoadmapParser.parse) consistent with existing RoadmapParser kept code predictable
- **Boolean doc flags** (has_ui_spec, etc.) followed existing has_context/has_plan convention, minimizing design decisions
- **Milestone audit before close** caught DOCS-07 rendering gap and Waves tab error message — both fixed before shipping

### What Was Inefficient
- **DOCS-07 gap** — continue_here field was wired backend-to-API but never rendered in frontend. Caught only by milestone audit, not during phase execution
- **Phase 11 missing VERIFICATION.md** — formal verification never run despite UAT existing. Process gap carried as tech debt
- **Hardcoded hex literals** — 36 found in UI-REVIEW, partially fixed. Token extraction should have been part of Phase 12 plan

### Patterns Established
- config.json presence as authoritative gsd-core detection signal (ROADMAP heading sniff as fallback)
- Section-bounded requirement parsing (scan only active milestone section, ignore Validated/Future)
- Fetch-once display-from-cache pattern for tab-based pages (fetch on segment change, not tab switch)
- Per-item useState accordion pattern for collapsible sections

### Key Lessons
1. **Run milestone audit before closing** — caught a real functional gap (DOCS-07) that would have shipped broken
2. **Frontend rendering gaps hide behind "field exists" checks** — a boolean field reaching api.ts doesn't mean it's displayed. E2E flow verification matters.
3. **Section-bounded parsing prevents false matches** — RequirementsParser initially captured 35 items instead of 21 because it scanned the full file including Validated section

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 8 | 15 | Initial MVP — established parser, discovery, dashboard patterns |
| v2.0 | 2 | 4 | Feature pages — TDD drift computation, shared utils extraction |
| v3.0 | 2 | 4 | gsd-core migration — new parser, doc surfacing, GSD-2 removal, insights page |

### Cumulative Quality

| Milestone | Tests | Key Metric |
|-----------|-------|------------|
| v1.0 | ~28 | Discovery, parser, settings coverage |
| v2.0 | ~35 | Drift computation TDD |
| v3.0 | 82 | +25 parser tests, +11 state parser progress tests |

### Top Lessons (Verified Across Milestones)

1. Static parser pattern (ClassName.parse(path) -> ParseResult) scales cleanly across parser types
2. Wave-based plan execution (backend first, frontend second) prevents integration rework
3. Milestone audit catches gaps that per-phase verification misses — always run before close
