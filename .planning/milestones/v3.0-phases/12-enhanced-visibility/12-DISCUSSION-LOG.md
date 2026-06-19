# Phase 12: Enhanced Visibility - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-18
**Phase:** 12-Enhanced Visibility
**Areas discussed:** Page structure, Requirements traceability, Wave visualization, Milestone archives

---

## Page Structure

| Option | Description | Selected |
|--------|-------------|----------|
| One new page | Single 'Insights' page with tabbed layout for requirements, waves, and archives. Keeps nav clean. | ✓ |
| Three separate pages | One page each for Requirements, Waves, and Archives. More nav items but each page is focused. | |
| Two pages | Requirements+Gaps on one page, Waves+Archives on another. Balanced approach. | |

**User's choice:** One new page with tabs
**Notes:** None

### Page Name

| Option | Description | Selected |
|--------|-------------|----------|
| Insights | Broad label covering requirements, waves, and archives | |
| Traceability | More specific to the primary feature | |
| You decide | Claude picks based on nav style | ✓ |

**User's choice:** You decide
**Notes:** Deferred to Claude's discretion

### Tab State

| Option | Description | Selected |
|--------|-------------|----------|
| Local state | Simple useState for active tab — matches existing page patterns | ✓ |
| URL hash | Hash fragments allow bookmarking specific tabs | |

**User's choice:** Local state
**Notes:** No deep-linking needed for desktop app

---

## Requirements Traceability

### Table Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Requirements-first | Rows are requirements, columns show phase and status. Gaps highlighted. | ✓ |
| Phases-first | Rows are phases, showing which requirements each covers | |
| Matrix view | Full cross-reference grid | |

**User's choice:** Requirements-first
**Notes:** None

### Gap Highlighting

| Option | Description | Selected |
|--------|-------------|----------|
| Color-coded row | Gap rows get red/amber background tint | ✓ |
| Icon + sort to top | Warning icon, sorted to top | |
| Both color + icon | Red-tinted row AND warning icon | |

**User's choice:** Color-coded row
**Notes:** Matches existing badge color patterns

### Data Source

| Option | Description | Selected |
|--------|-------------|----------|
| Parse REQUIREMENTS.md table | New parser extracts traceability table | ✓ |
| Derive from ROADMAP.md | Extract requirement IDs from phase entries | |
| You decide | Claude picks | |

**User's choice:** Parse REQUIREMENTS.md table
**Notes:** Single source of truth

### Grouping

| Option | Description | Selected |
|--------|-------------|----------|
| Grouped by category | Section headers matching REQUIREMENTS.md headings | ✓ |
| Flat list, sorted by ID | All requirements in one table | |
| You decide | Claude picks | |

**User's choice:** Grouped by category
**Notes:** None

---

## Wave Visualization

### Display Format

| Option | Description | Selected |
|--------|-------------|----------|
| Wave table | Table grouped by phase, showing plan-to-wave assignments | ✓ |
| Swimlane diagram | Visual timeline with horizontal lanes per wave | |
| You decide | Claude picks simplest approach | |

**User's choice:** Wave table
**Notes:** None

### Filter

| Option | Description | Selected |
|--------|-------------|----------|
| All phases with plans | Show every phase that has plans | |
| Multi-wave only | Only phases with 2+ waves | ✓ |
| You decide | Claude picks | |

**User's choice:** Multi-wave only
**Notes:** Single-wave phases uninteresting for this view

### Data Source

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing plan parsing | PlanParser already reads frontmatter; add wave extraction | ✓ |
| You decide | Claude picks | |

**User's choice:** Extend existing plan parsing
**Notes:** None

---

## Milestone Archives

### Display Format

| Option | Description | Selected |
|--------|-------------|----------|
| Collapsed accordion | Each shipped milestone collapsible, expand to see phases | ✓ |
| Timeline/cards | Each milestone as a card with summary stats | |
| You decide | Claude picks | |

**User's choice:** Collapsed accordion
**Notes:** Matches existing collapsible patterns

### Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Shipped only | Archives tab is purely historical | ✓ |
| All milestones | Active milestone at top plus shipped ones below | |

**User's choice:** Shipped only
**Notes:** Active milestone already visible on Dashboard

---

## Claude's Discretion

- Nav label for the new page (D-12)
- Backend API design — new endpoints vs extending existing response (D-13)
- Tab styling and component structure (D-14)

## Deferred Ideas

None — discussion stayed within phase scope
