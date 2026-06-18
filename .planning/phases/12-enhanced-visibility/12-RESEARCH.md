# Phase 12: Enhanced Visibility — Research

**Researched:** 2026-06-18
**Domain:** GSD Monitor — parsing, backend API extension, React feature page
**Confidence:** HIGH (all findings from direct codebase inspection)

---

## 1. REQUIREMENTS.md Traceability Format

### File location
`.planning/REQUIREMENTS.md` — read directly during research.

### Structure
REQUIREMENTS.md has two relevant sections:

**Inline requirement checkboxes** (grouped under `### Category` headings):
```
### Detection & Parsing

- [x] **DETECT-01**: Monitor detects gsd-core projects via .planning/config.json presence
- [x] **DETECT-02**: Monitor parses gsd-core ROADMAP.md heading-based phase format
```

Each line: `- [x] **{ID}**: {description}` where `[x]` = complete, `[ ]` = not yet done.

**Traceability table** (under `## Traceability`):
```markdown
| Requirement | Phase | Status |
|-------------|-------|--------|
| DETECT-01 | Phase 11 | Complete |
| VIS-01 | Phase 12 | Pending |
```

Three columns: `Requirement` (e.g. `DETECT-01`), `Phase` (e.g. `Phase 11`), `Status` (`Complete` or `Pending`).

**Coverage block** that follows:
```
**Coverage:**
- v3.0 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0
```

### Parsing strategy for VIS-01 / VIS-04
A new `RequirementsParser` should:
1. Walk the file looking for `### ` category headings — capture the category name for grouping (D-06).
2. Within each category, match `- [x] **{ID}**: {description}` lines to collect all requirements with their IDs and descriptions.
3. Parse the `## Traceability` table to build `{ID → phase, status}` mappings.
4. Join the two: for each requirement, attach the traceability row. Requirements with no row in the traceability table are **unmapped gaps** (VIS-04).

**Regex patterns needed:**
```python
_CATEGORY_HDR = re.compile(r"^###\s+(.+)$", re.MULTILINE)
_REQ_LINE = re.compile(r"^-\s*\[([x ])\]\s*\*\*([A-Z]+-\d+)\*\*:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_TRACE_ROW = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$", re.MULTILINE)
```

### Current file state (from actual REQUIREMENTS.md)
Categories: `Detection & Parsing`, `Document Surfacing`, `Progress & State`, `Enhanced Visibility`.
Total requirements with traceability: 21. All mapped. VIS-01/02/03/04 are `Pending` in Phase 12.

---

## 2. Existing Parser Patterns

### 2a. PlanParser — current state and wave field

**File:** `gsd_monitor/parsers/plan_parser.py`

Current `PlanParser` reads only the **body** of PLAN.md for the H1 title and task checkboxes. It **does not read YAML frontmatter at all** — it uses a plain `_H1` regex on the full text (frontmatter included, harmlessly skipped because frontmatter rarely contains `# `).

**Wave field is already in frontmatter** of all existing plans:
```yaml
---
phase: 11-gsd-core-support
plan: 02
type: execute
wave: 2
depends_on:
  - 11-01
---
```

Confirmed in: `11-01-PLAN.md` (wave: 1), `11-02-PLAN.md` (wave: 2), `10-01-PLAN.md` (wave: 1), `10-02-PLAN.md` (wave: 2), `10-03-PLAN.md` (wave: 2).

**`_FRONTMATTER` regex exists in `project_discovery.py`** (line 32):
```python
_FRONTMATTER = re.compile(r"^---\s*\n.*?^---\s*\n", re.DOTALL | re.MULTILINE)
```
And it already strips frontmatter for `plan_content` display. But the frontmatter is never parsed for structured fields.

**Extension required:** `PlanParser.parse()` must be extended (or a helper added) to also extract `wave: N` from the YAML frontmatter block. Return `wave: int | None` alongside existing title/todos.

### 2b. GsdCoreRoadmapParser — archived milestone parsing

**File:** `gsd_monitor/parsers/gsd_core_roadmap.py`

`_extract_archived_milestones(text, phase_map)` already:
- Finds all `<details>...</details>` blocks using `_DETAILS_OPEN` / `_DETAILS_CLOSE` regexes
- Extracts `<summary>Title</summary>` as the milestone title
- Extracts phases from the block using `_HEADING_PHASE` (heading format) or `_CHECKBOX_PHASE` (checkbox format) — whichever matches
- Returns `list[Milestone]` with `status = SHIPPED` (via `_determine_milestone_status`)

**From the actual ROADMAP.md**, the archived milestone block looks like:
```html
<details>
<summary>v2.0 — Feature Pages (Phases 9-10) — SHIPPED 2026-04-12</summary>

### Phases

- [x] **Phase 9: Drift Computation** - Backend computes real DriftIndicator ...
- [x] **Phase 10: Feature Pages** - Drift, Quick Tasks, and Verification pages ...
...
</details>
```

The parser calls `_determine_milestone_status(summary_title, phase_entries)` — the `_EMOJI_COMPLETED` regex matches "SHIPPED" so these milestones get `MilestoneStatus.COMPLETED`.

**Data already flows through API:** `GsdProject.milestones` includes archived milestones at the end of the list (after non-archived ones). The `_parse_milestones` method appends them with `Milestone(number=ms_count, ...)`. The frontend already receives them in `milestones` array within `GsdProjectPayload`.

**Gap for VIS-03:** No field currently distinguishes archived milestones from active ones at the `Milestone` model level. The frontend cannot filter "shipped only" without additional data. Options:
1. Add `is_archived: bool` to `Milestone` model (mirrors `PhaseEntry.is_archived` pattern).
2. Rely on `status == "completed"` — but active milestones can also be `completed`.
3. Add a `completion_date: str | None` field extracted from the summary line.

Best approach: add `is_archived: bool = False` to `Milestone` and set it `True` in `_extract_archived_milestones()`. The completion date text from the summary (e.g. `"SHIPPED 2026-04-12"`) can optionally be stored as `completion_date: str | None`.

### 2c. RoadmapParser (legacy) — archive parsing

**File:** `gsd_monitor/parsers/roadmap.py`

`_try_extract_from_milestone_archives()` reads `milestones/v1.0-ROADMAP.md`, `milestones/v2.0-ROADMAP.md`, etc. — separate files, not `<details>` blocks. These are GSD-1 format archives only. Not relevant for VIS-03 (gsd-core projects use `<details>` blocks in the main ROADMAP.md).

---

## 3. Model Analysis

### 3a. PhaseEntry (current fields)

All fields relevant to this phase are already present:
- `number`, `title`, `status`, `goal`, `code` — display fields
- `is_archived: bool`, `archive_milestone: str | None` — already track archive state
- `has_requirements: bool` — project-level flag (True if `REQUIREMENTS.md` exists)
- `depends_on: list[str]` — present but not populated by current `_enrich_phase()`

**New fields needed on PhaseEntry:**
- `wave: int | None = None` — extracted from PLAN.md frontmatter; surfaced to frontend for VIS-02

### 3b. Milestone (current fields)

```python
class Milestone(BaseModel):
    title: str = ""
    number: int = 0
    status: MilestoneStatus = MilestoneStatus.PLANNED
    progress: int = 0
    phases: list[PhaseEntry] = Field(default_factory=list)
    code: str | None = None
    vision: str | None = None
```

**New fields needed on Milestone:**
- `is_archived: bool = False` — needed so frontend can filter to archived-only for VIS-03 Archives tab
- `completion_date: str | None = None` — optional; extracted from `<summary>` text (e.g. `"SHIPPED 2026-04-12"`)

### 3c. GsdProject (current fields)

No changes needed. The traceability data comes from REQUIREMENTS.md directly, not from `GsdProject`.

### 3d. New model needed: RequirementEntry

```python
class RequirementEntry(BaseModel):
    id: str           # "VIS-01"
    category: str     # "Enhanced Visibility"
    description: str  # Full text after ":"
    is_checked: bool  # from - [x] or - [ ]
    phase: str | None # "Phase 12" from traceability table
    status: str | None # "Pending" / "Complete" from traceability table
    is_gap: bool      # True when no entry in traceability table
```

This can live in `models/core.py` or be a local dataclass in the new parser file.

---

## 4. Discovery & Data Flow

### 4a. How _enrich_phase() works

`_enrich_phase(planning_dir, phases_dir, phase)` (lines 431-547 of `project_discovery.py`):

1. Resolves `phase_dir` by matching `f"{phase.number:02d}-*"` directories under `phases/`
2. Falls back to `_find_archive_phase_dir()` for archived phases
3. Reads `*-PLAN.md` files — calls `PlanParser.parse(latest_plan)`
4. Reads mtime, artifact paths, computes drift
5. Checks for `CONTEXT.md`, `RESEARCH.md`, `UAT.md`, etc. via `.is_file()` checks
6. Returns a fully enriched `PhaseEntry`

**Wave extraction point:** After `pr = PlanParser.parse(str(latest_plan))`, extend to also extract wave from frontmatter. Pass wave through to the returned `PhaseEntry`.

**Alternatively**, to get wave for ALL plan files (not just latest), iterate `plan_files` and extract wave from each, building a `{filename → wave}` map. This is needed for wave grouping (D-07/D-08).

### 4b. Current data flow for traceability

There is **no current mechanism** to pass REQUIREMENTS.md parsed data to the frontend. It is not parsed at all during discovery. Two options:

**Option A (preferred, per D-13): Extend existing /api/groups response**
- Parse REQUIREMENTS.md during `_build_gsd1_segment()` or `_enrich_planning()`
- Add `requirements: list[RequirementEntry]` to `GsdProject`
- Frontend gets it in the existing groups payload

**Option B: New endpoint `/api/insights/{planning_path}`**
- Parse on demand when frontend loads Insights page
- Lighter discovery path; no model changes

Given D-13 says "path of least resistance" and the data is small + already cached during refresh, Option A keeps patterns consistent with how `plan_content`, `research_content`, etc. are surfaced. Option B avoids growing the groups response for data only one tab needs.

**Recommendation: Option B (new on-demand endpoint)** — REQUIREMENTS.md parsing is expensive only once per request, the data is only needed for the Insights page, and the groups response is already large. An endpoint `/api/insights/{planning_path:path}` returning `{requirements, waves}` is clean and doesn't bloat the existing data structure.

### 4c. Wave data flow

Wave data lives in PLAN.md frontmatter. During `_enrich_phase()`, only the latest PLAN is read. For wave grouping we need all plans' wave assignments.

**Approach:** In `_enrich_phase()`, iterate ALL `plan_files`, extract `(plan_name, wave)` from each frontmatter. Store as a list of `PlanWaveEntry` objects. Include in `PhaseEntry` as `plan_waves: list[PlanWaveEntry] = Field(default_factory=list)`.

Alternatively: surface via the new `/api/insights` endpoint by reading all plan files in `phases_dir` directly (no model changes, simpler).

**Recommendation: Include wave data in the new `/api/insights` endpoint** to avoid adding a potentially-large list field to PhaseEntry that is unused by all other pages.

### 4d. Archive data flow for VIS-03

Archived milestones are already in `project.milestones` (at the end, with no ordering guarantee). The frontend already receives them via `GsdProjectPayload.milestones`. What's missing:
- A way to tell archived milestones apart from active ones
- Optionally, a completion date string

This requires the `Milestone` model change (`is_archived: bool`) described in section 3b.

---

## 5. Frontend Patterns

### 5a. Page pattern (from DriftPage, VerificationPage)

All feature pages follow this exact structure:
```tsx
import { useMemo, useState } from "react";
import { useApp } from "../context";
import type { PhasePayload } from "../api";

export function InsightsPage() {
  const { activeProject, activeSegment, loading } = useApp();
  const [activeTab, setActiveTab] = useState<"requirements" | "waves" | "archives">("requirements");

  if (loading) return <div className="p-6 text-[#858585] text-sm">Loading…</div>;
  if (!activeProject)
    return <div className="p-6 text-[#858585] text-sm">Add scan roots in Settings and select a project.</div>;

  return (
    <div className="p-6">
      {/* tab bar */}
      {/* tab content */}
    </div>
  );
}
```

Named export, no default export. Data from `useApp()` context only. Local `useState` for UI-only concerns.

### 5b. Color conventions (from DriftPage, VerificationPage)

| Color class | Usage |
|-------------|-------|
| `bg-red-900/40 text-red-400` | Error, gap, major drift |
| `bg-yellow-900/40 text-yellow-400` | Warning, minor drift, pending |
| `bg-green-900/40 text-[#4ec994]` | Success, complete, pass |
| `bg-[#2a2d2e] text-[#858585]` | Neutral, deferred, unknown |

Gap rows (VIS-04): `bg-red-900/20` full row tint, or `bg-amber-900/20` for pending-but-mapped rows. Red for truly unmapped, amber for pending-but-has-a-phase is the likely differentiation.

### 5c. Table pattern

No existing page uses an HTML `<table>` — all use `div.space-y-2` cards. For requirements traceability (a true tabular structure), `<table>` with `border-collapse` is appropriate and precedented for markdown-rendered content. Use Tailwind `table-auto`, `border-[#474747]` cells.

### 5d. Collapsible section pattern (from VerificationPage)

```tsx
const [showSection, setShowSection] = useState(false);

<button
  type="button"
  className="mt-4 flex items-center gap-1 text-xs text-[#858585] hover:text-[#cccccc]"
  onClick={() => setShowSection((v) => !v)}
  aria-expanded={showSection}
>
  <span>{showSection ? "⌄" : "›"}</span>
  <span>{showSection ? "Hide section" : `Show N items`}</span>
</button>
{showSection && (
  <div className="mt-2 space-y-2">...</div>
)}
```

Use this pattern for Archives accordion items (VIS-03 — collapsed by default, expand to see phase list).

### 5e. Tab bar pattern

No existing tab bar in the codebase. Implement as a local horizontal pill pattern consistent with existing nav:

```tsx
const TABS = [
  { id: "requirements", label: "Requirements" },
  { id: "waves", label: "Waves" },
  { id: "archives", label: "Archives" },
] as const;

type TabId = typeof TABS[number]["id"];

// Render:
<div className="mb-6 flex gap-1 border-b border-[#474747] pb-2">
  {TABS.map((tab) => (
    <button
      key={tab.id}
      type="button"
      onClick={() => setActiveTab(tab.id)}
      className={`rounded-md px-3 py-1.5 text-sm font-medium ${
        activeTab === tab.id
          ? "bg-[#2a2d2e] text-[#cccccc]"
          : "text-[#858585] hover:bg-[#2a2d2e] hover:text-[#cccccc]"
      }`}
    >
      {tab.label}
    </button>
  ))}
</div>
```

This matches the `ShellLayout` NavLink styling idiom.

### 5f. Navigation — ShellLayout.tsx

Current nav array (lines 6-13 of ShellLayout.tsx):
```ts
const nav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/docs", label: "Docs" },
  { to: "/drift", label: "Drift" },
  { to: "/quick-tasks", label: "Quick Tasks" },
  { to: "/verification", label: "Verification" },
  { to: "/settings", label: "Settings" },
];
```

Add `{ to: "/insights", label: "Insights" }` between "Verification" and "Settings" (D-12 decides the label — "Insights" fits the pattern of short single-word labels).

### 5g. React Router — App.tsx and main.tsx

`App.tsx` uses `<Routes>` from react-router-dom. Adding a new route:
```tsx
import { InsightsPage } from "./pages/InsightsPage";
// ...
<Route path="/insights" element={<InsightsPage />} />
```

`main.tsx` only wraps in `BrowserRouter` — no changes needed there.

### 5h. API client — api.ts

New interfaces needed:
```ts
export interface RequirementEntryPayload {
  id: string;            // "VIS-01"
  category: string;      // "Enhanced Visibility"
  description: string;
  is_checked: boolean;
  phase: string | null;  // "Phase 12"
  status: string | null; // "Complete" / "Pending"
  is_gap: boolean;       // true if not in traceability table
}

export interface PlanWaveEntry {
  plan_name: string;     // "11-01-PLAN.md"
  wave: number;
}

export interface PhaseWavePayload {
  phase_number: number;
  phase_title: string;
  plans: PlanWaveEntry[];
}

export interface InsightsPayload {
  requirements: RequirementEntryPayload[];
  wave_phases: PhaseWavePayload[];   // only phases with >1 wave
}

export async function fetchInsights(planningPath: string): Promise<InsightsPayload> {
  const enc = encodeURIComponent(planningPath);
  const r = await fetch(`${base}/api/insights/${enc}`, noStore);
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<InsightsPayload>;
}
```

The `MilestonePayload` interface needs the new archived-milestone fields:
```ts
export interface MilestonePayload {
  title: string;
  number: number;
  status: string;
  progress: number;
  phases: PhasePayload[];
  code?: string | null;
  vision?: string | null;
  is_archived?: boolean;         // NEW — for VIS-03 Archives tab
  completion_date?: string | null; // NEW — optional date from summary text
}
```

---

## 6. API Analysis

### 6a. Current endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Healthcheck |
| GET | `/api/groups` | All discovered project groups |
| POST | `/api/groups/refresh` | Re-scan and return groups |
| GET | `/api/settings` | Current settings |
| PUT | `/api/settings` | Save settings |
| POST | `/api/browse-folder` | pywebview folder picker |
| GET | `/api/quick-tasks/{planning_path}` | Quick tasks for a planning path |
| GET | `/api/docs/{planning_path}/tree` | Doc tree for a planning path |
| GET | `/api/docs/{planning_path}/file` | Read a doc file |
| WS | `/ws/events` | WebSocket push events |

### 6b. New endpoint needed

**`GET /api/insights/{planning_path:path}`**

Pattern matches `/api/quick-tasks/{planning_path:path}` exactly.

Implementation:
```python
@application.get("/api/insights/{planning_path:path}")
async def insights(planning_path: str) -> dict[str, Any]:
    from urllib.parse import unquote
    p = unquote(planning_path)
    reqs = RequirementsParser.parse(p)
    waves = _extract_wave_data(p)
    return {
        "requirements": [r.model_dump(mode="json") for r in reqs],
        "wave_phases": waves,
    }
```

`RequirementsParser.parse(planning_path)` reads `{planning_path}/REQUIREMENTS.md`.
`_extract_wave_data(planning_path)` reads all `phases/*/NN-NN-PLAN.md` files for frontmatter.

### 6c. Backend data contract for wave data

`_extract_wave_data(planning_dir: str)` needs to:
1. Walk `phases/*/` subdirectories
2. For each PLAN.md in a phase dir, extract `wave: N` from frontmatter
3. Group by phase number
4. Filter to phases that have plans in more than one wave value
5. Return as list of `PhaseWavePayload` dicts

This is a pure read operation, runs in endpoint handler (not discovery path).

### 6d. Backend data contract for archived milestones

For VIS-03 the archived milestones are already in `GsdProject.milestones` via `GsdCoreRoadmapParser._extract_archived_milestones()`. The only backend change is:
- Add `is_archived: bool = False` and `completion_date: str | None = None` to `Milestone` model
- Set `is_archived=True` in `_extract_archived_milestones()` for each returned `Milestone`
- Optionally parse `"SHIPPED 2026-04-12"` from summary text with a simple regex

No new endpoint needed for VIS-03 — the data rides in the existing `/api/groups` response through `GsdProjectPayload.milestones`.

---

## 7. Implementation Approach

### VIS-01 & VIS-04 — Requirements Traceability Table

**Backend (new file: `gsd_monitor/parsers/requirements_parser.py`)**:
- Class `RequirementsParser` following static `parse(planning_dir: str) -> list[RequirementEntry]` pattern
- Reads `{planning_dir}/REQUIREMENTS.md`
- Returns empty list if file not found (graceful degradation)
- Uses three regex passes: category headers, requirement lines, traceability table rows
- Joins them: each `RequirementEntry` gets `category`, `description`, `phase`, `status`, `is_gap`

**Backend (new endpoint in `gsd_monitor/api/app.py`)**:
- `GET /api/insights/{planning_path:path}` — mirrors quick-tasks endpoint pattern
- Calls `RequirementsParser.parse(p)` for requirements
- Calls a wave-data helper for plan wave assignments

**Frontend (new page `frontend/src/pages/InsightsPage.tsx`)**:
- Three-tab layout (Requirements, Waves, Archives)
- Requirements tab: table grouped by category, gap rows highlighted red/amber
- Fetch via `fetchInsights(activeSegment.planningPath)` when tab becomes active
- `useEffect` with dependency on `[activeSegment?.planningPath, activeTab]`

### VIS-02 — Wave Visualization

**Backend**: `_extract_wave_data(planning_dir)` function in `app.py` (or in a new helper module). Reads `phases/*/NN-PLAN.md` frontmatter, groups by phase, filters to multi-wave phases only (D-08).

**Frontend**: Waves tab shows a table: Phase number + title | Wave 1 plans | Wave 2 plans | ... The "parallel" relationship is expressed by showing same-wave plans side by side or in a grouped row.

### VIS-03 — Milestone Archive Browsing

**Backend**:
- Add `is_archived: bool = False` and `completion_date: str | None = None` to `Milestone` model in `core.py`
- In `GsdCoreRoadmapParser._extract_archived_milestones()`, set `is_archived=True` on returned milestones
- Optionally add a simple regex `_SHIPPED_DATE = re.compile(r"SHIPPED\s+([\d\-]+)")` to extract date from summary

**Frontend**: Archives tab filters `activeProject.milestones` by `is_archived === true`. Renders as collapsed accordion — each item shows milestone title + completion_date (or "date unknown"). Expand to see phase list.

### Nav + Routing

- `ShellLayout.tsx`: add `{ to: "/insights", label: "Insights" }` to `nav` array
- `App.tsx`: add `<Route path="/insights" element={<InsightsPage />} />` and import

---

## Summary of Changes Required

### New files
| File | Purpose |
|------|---------|
| `gsd_monitor/parsers/requirements_parser.py` | Parse REQUIREMENTS.md traceability data |
| `frontend/src/pages/InsightsPage.tsx` | New three-tab Insights page |

### Modified files
| File | Change |
|------|--------|
| `gsd_monitor/models/core.py` | Add `wave: int | None` to `PhaseEntry`; add `is_archived: bool`, `completion_date: str | None` to `Milestone` |
| `gsd_monitor/parsers/plan_parser.py` | Extract `wave` field from YAML frontmatter |
| `gsd_monitor/parsers/gsd_core_roadmap.py` | Set `is_archived=True` on archived milestones; optionally extract `completion_date` |
| `gsd_monitor/services/project_discovery.py` | Wire `wave` from `PlanParser` into `PhaseEntry` in `_enrich_phase()` |
| `gsd_monitor/api/app.py` | Add `GET /api/insights/{planning_path:path}` endpoint |
| `frontend/src/api.ts` | Add `InsightsPayload`, `RequirementEntryPayload`, `PhaseWavePayload`, `PlanWaveEntry` interfaces; extend `MilestonePayload`; add `fetchInsights()` |
| `frontend/src/ShellLayout.tsx` | Add Insights nav item |
| `frontend/src/App.tsx` | Add `/insights` route and import |

---

## RESEARCH COMPLETE

**Confidence:** HIGH — all findings from direct inspection of source files.

**Key facts confirmed:**
- Wave field is already present in every PLAN.md frontmatter; `PlanParser` does not currently read frontmatter at all — needs extension
- Archived milestones are already parsed by `GsdCoreRoadmapParser._extract_archived_milestones()` and flow through the groups API; the only missing piece is an `is_archived` flag on `Milestone`
- REQUIREMENTS.md traceability table is a clean 3-column markdown table — straightforward to regex-parse
- No tab bar component exists in the codebase — must be built inline following ShellLayout NavLink style conventions
- The natural API extension is a new `/api/insights/{planning_path}` endpoint mirroring the `/api/quick-tasks/{planning_path}` pattern exactly
- `nyquist_validation` is `false` in `.planning/config.json` — no test framework section required
