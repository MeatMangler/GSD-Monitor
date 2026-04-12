# Phase 10: Feature Pages — Research

**Researched:** 2026-04-12
**Domain:** React 19 / TypeScript / Tailwind CSS v4 — frontend feature pages consuming existing FastAPI data
**Confidence:** HIGH

---

## Summary

Phase 10 is a pure frontend phase. The backend already delivers all required data: `drift`, `has_validation`, `nyquist_compliant`, `has_uat`, `validation_content`, and quick-task fields are all computed and serialized by Phase 9 and earlier work. The three stub pages (`DriftPage`, `QuickTasksPage`, `VerificationPage`) exist as empty placeholders and need only their bodies replaced — routing, nav registration, and context plumbing are already complete.

The one genuine data-layer decision is whether to expose `plan_write_time` to the TypeScript layer. The field is present in the Pydantic model and is serialized to JSON by `model_dump_json()`, so it arrives in the API response today. The only gap is the missing declaration in `PhasePayload` in `api.ts`. Adding `plan_write_time?: string | null` to that interface unblocks DRFT-03 plan-age display with zero backend changes.

Shared helper functions `fmtDate()` and `statusLabel()` are currently defined inside `DashboardPage.tsx`. Both are needed by all three new pages. The executor must extract these to `src/utils.ts` before implementing the pages — this is confirmed in the UI-SPEC and is a prerequisite, not optional cleanup.

**Primary recommendation:** Implement the three pages in one plan containing four tasks: (1) extract shared utils, (2) wire `plan_write_time` in `api.ts`, (3) implement DriftPage, (4) implement QuickTasksPage, (5) implement VerificationPage. Tasks 3-5 can be issued as three separate plans or combined, each self-contained after tasks 1-2 complete.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DRFT-02 | DriftPage displays per-phase drift table, sorted MAJOR first | `activeProject.milestones.flatMap(m => m.phases)` available in context; drift field is `string` enum on `PhasePayload`; sort is client-side |
| DRFT-03 | Each drift row shows phase number, title, status, drift badge, plan age, last updated | `plan_write_time` is in API JSON but not in `PhasePayload` TS interface — requires one-line addition; `fmtDate()` and `statusLabel()` must move to utils |
| DRFT-04 | Drift badges color-coded MAJOR=red, MINOR=yellow, NONE=green, DEFERRED=gray | Badge color map documented in UI-SPEC; uses exact Tailwind classes from existing badge pattern |
| DRFT-05 | Phases with not_started status and deferred drift collapsed behind toggle | `useState` toggle; filter on `status === "not_started" && drift === "deferred"`; revealed rows get `opacity-60` |
| QTSK-01 | QuickTasksPage fetches from `/api/quick-tasks/{planningPath}` | `fetchQuickTasks()` already in `api.ts`; fetched on mount and `activeSegment` change via `useEffect` |
| QTSK-02 | Each task row shows title, status badge, created date, last updated date | `QuickTaskPayload` interface already in `api.ts` with all required fields |
| QTSK-03 | Status badges color-coded open=gray, in_progress=yellow, complete=green | Badge color map in UI-SPEC; same badge pattern as drift |
| QTSK-04 | Empty state shown when no tasks exist | `tasks.length === 0` after loading; not an error state |
| QTSK-05 | Tasks sorted by last_updated descending | Client-side sort; `byLastUpdated()` sort function from DashboardPage can be reused in utils |
| VERIF-01 | VerificationPage shows per-phase verification summary | Same data source as DriftPage — `activeProject.milestones.flatMap(m => m.phases)` |
| VERIF-02 | Each row shows phase number, title, has_validation badge, nyquist_compliant badge, has_uat badge | All three boolean fields already on `PhasePayload`; badge color map in UI-SPEC |
| VERIF-03 | Clicking a row expands inline to show validation_content as markdown | `useState<number | null>` for expanded phase number; `validation_content` already on `PhasePayload`; `ReactMarkdown + remarkGfm` already imported in DashboardPage — follow same pattern |
| VERIF-04 | Phases without validation file dimmed and hidden behind toggle | `has_validation === false` filter; toggle pattern identical to DRFT-05; `opacity-60` on revealed rows |
</phase_requirements>

---

## Project Constraints (from CLAUDE.md)

- **Tech stack locked:** Python 3.11+ / FastAPI / pywebview / React 19 / Tailwind CSS v4 / Vite 6 — no stack changes
- **No new npm packages:** UI-SPEC Registry Safety explicitly states "No new npm packages, no new registries, no third-party component blocks." All three pages use only existing dependencies.
- **Read-only app:** Phase must not introduce any write paths. No confirmation dialogs, no form submissions to project files.
- **TypeScript strict mode:** `tsconfig.json` has `"strict": true`, `"noUnusedLocals": true`, `"noUnusedParameters": true` — all types must be complete, no unused imports.
- **Named exports only:** No default exports for pages or components (App.tsx is the one exception).
- **Tailwind CSS v4:** No `tailwind.config.js`. Uses `@tailwindcss/vite` plugin. All classes must be utility-only — no `@apply` or custom classes.
- **No CSS modules or styled components:** Utility classes inline only.
- **`void` prefix on fire-and-forget async calls:** e.g., `void reload()`, `void fetchQuickTasks(...)`.
- **`useCallback` on stable references:** reload is already stable; `fetchQuickTasks` calls should follow the project's async/await pattern.
- **`useMemo` for derived values from context:** Phase lists derived from `activeProject.milestones.flatMap(...)` must use `useMemo`.
- **nyquist_validation is explicitly false** in `.planning/config.json` — Validation Architecture section is omitted.
- **GSD workflow enforcement:** Changes to repo files must go through GSD workflow entry points.

---

## Standard Stack

### Core (all already in package.json — zero new installs)

[VERIFIED: codebase grep of frontend/package.json and frontend/src/]

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| React 19 | 19.0 | Component rendering, useState, useMemo, useEffect, useCallback | Already installed |
| TypeScript 5.9 | 5.9 | Static typing, strict mode | Already installed |
| Tailwind CSS v4 | 4.0 | Utility styling via @tailwindcss/vite | Already installed |
| react-markdown | 10.0 | Renders `validation_content` markdown inline (VERIF-03) | Already installed, already imported in DashboardPage |
| remark-gfm | 4.0 | GitHub Flavored Markdown tables/strikethrough in validation content | Already installed, already imported in DashboardPage |
| react-router-dom | 7.0 | Navigation already wired; pages are already registered | Already installed |

**Installation:** No installation step needed. All dependencies exist.

---

## Architecture Patterns

### Data Access Pattern

All three pages consume data already in React context (`AppCtx`). No new API endpoints, no new context fields.

```typescript
// VERIFIED: frontend/src/context.tsx
// activeProject: SegmentPayload["project"] | null
// activeSegment: SegmentPayload | null
const { activeProject, activeSegment, loading } = useApp();

// Phase data — use useMemo per project conventions
const phases = useMemo(
  () => activeProject?.milestones.flatMap((m) => m.phases) ?? [],
  [activeProject],
);
```

### QuickTasks Fetch Pattern

[VERIFIED: frontend/src/api.ts — `fetchQuickTasks` exists, `QuickTaskPayload` is defined]

```typescript
// VERIFIED: frontend/src/api.ts
export async function fetchQuickTasks(planningPath: string): Promise<QuickTaskPayload[]>;

// Fetch on mount and on activeSegment change:
useEffect(() => {
  if (!activeSegment?.planningPath) return;
  setLoading(true);
  void fetchQuickTasks(activeSegment.planningPath)
    .then((t) => { setTasks(t); setError(null); })
    .catch(() => setError("Could not load quick tasks. Check your project path and try refreshing."))
    .finally(() => setLoading(false));
}, [activeSegment?.planningPath]);
```

### Shared Utils Extraction (Prerequisite)

[VERIFIED: frontend/src/pages/DashboardPage.tsx lines 17-45 — fmtDate, statusLabel, byLastUpdated, statusBorderClass all defined inline]

These four functions must move to `frontend/src/utils.ts` before the new pages are written:

- `fmtDate(d: string | null | undefined): string` — date display
- `statusLabel(s: string): string` — human-readable status
- `byLastUpdated(a, b): number` — sort comparator
- `statusBorderClass(status: string): string` — left accent border color

`DashboardPage.tsx` is then updated to import from `../utils` instead of defining them inline. The new pages import from the same location.

### plan_write_time Data Layer Fix

[VERIFIED: gsd_monitor/models/core.py line 32 — `plan_write_time: datetime | None = None` on PhaseEntry]
[VERIFIED: gsd_monitor/api/app.py line 138 — `json.loads(seg.project.model_dump_json())` serializes all Pydantic fields including plan_write_time]
[VERIFIED: frontend/src/api.ts lines 114-138 — `PhasePayload` interface does NOT include `plan_write_time`]

The field is present in the JSON response today. Only the TypeScript interface needs updating:

```typescript
// Add to PhasePayload in frontend/src/api.ts:
plan_write_time?: string | null;
```

Plan age in days (for DRFT-03):
```typescript
function planAgeDays(plan_write_time: string | null | undefined): number | null {
  if (!plan_write_time) return null;
  return Math.floor((Date.now() - new Date(plan_write_time).getTime()) / 86_400_000);
}
// Display: age !== null ? `${age} day${age === 1 ? "" : "s"}` : "—"
```

### Collapsible Section Pattern

[VERIFIED: frontend/src/pages/DocsPage.tsx — expand/collapse with `›` / `⌄` glyphs and aria-expanded]
[VERIFIED: 10-UI-SPEC.md — identical toggle pattern for DRFT-05 and VERIF-04]

```tsx
// Pattern for DRFT-05 and VERIF-04:
const [showHidden, setShowHidden] = useState(false);
const hiddenPhases = phases.filter(p => p.status === "not_started" && p.drift === "deferred");
const visiblePhases = phases.filter(p => !(p.status === "not_started" && p.drift === "deferred"));

// Toggle button:
<button
  type="button"
  className="mt-4 flex items-center gap-1 text-xs text-[#858585] hover:text-[#cccccc]"
  onClick={() => setShowHidden(v => !v)}
  aria-expanded={showHidden}
  aria-controls="hidden-phases"
>
  <span>{showHidden ? "⌄" : "›"}</span>
  <span>{showHidden ? "Hide un-started phases" : `Show ${hiddenPhases.length} un-started phases`}</span>
</button>
{showHidden && (
  <div id="hidden-phases" className="mt-2 space-y-2 opacity-60">
    {hiddenPhases.map(p => /* row */)}
  </div>
)}
```

### Inline Expand Pattern (VerificationPage VERIF-03)

[VERIFIED: frontend/src/pages/DocsPage.tsx — directory expand/collapse with aria-expanded]

```tsx
const [expandedPhase, setExpandedPhase] = useState<number | null>(null);

// In row:
<button
  type="button"
  className="w-full ..."
  onClick={() => phase.has_validation
    ? setExpandedPhase(n => n === phase.number ? null : phase.number)
    : undefined
  }
  aria-expanded={expandedPhase === phase.number}
>
  <span className="text-xs text-[#858585]">
    {phase.has_validation ? (expandedPhase === phase.number ? "⌄" : "›") : " "}
  </span>
  {/* rest of row */}
</button>
{expandedPhase === phase.number && phase.validation_content && (
  <div className="prose prose-invert prose-sm max-w-none border-t border-[#474747] p-4">
    <ReactMarkdown remarkPlugins={[remarkGfm]}>{phase.validation_content}</ReactMarkdown>
  </div>
)}
```

### Badge Pattern

[VERIFIED: frontend/src/pages/DashboardPage.tsx — badge rendering in phase rows]
[VERIFIED: 10-UI-SPEC.md Semantic Badge Colors section]

```tsx
// All badges follow this pattern:
<span className={`rounded px-1.5 py-0.5 text-xs font-medium ${colorClasses}`}>
  {label}
</span>

// Drift badge color map:
function driftBadgeClass(drift: string): string {
  switch (drift) {
    case "major":   return "bg-red-900/40 text-red-400";
    case "minor":   return "bg-yellow-900/40 text-yellow-400";
    case "none":    return "bg-green-900/40 text-[#4ec994]";
    default:        return "bg-[#2a2d2e] text-[#858585]"; // deferred
  }
}

// Quick task status badge color map:
function taskStatusBadgeClass(status: string): string {
  switch (status) {
    case "in_progress": return "bg-yellow-900/40 text-yellow-400";
    case "complete":    return "bg-green-900/40 text-[#4ec994]";
    default:            return "bg-[#2a2d2e] text-[#858585]"; // open
  }
}
```

### Drift Sort Order

[VERIFIED: REQUIREMENTS.md DRFT-02 — MAJOR first, then MINOR, then NONE/DEFERRED]

```typescript
const DRIFT_ORDER: Record<string, number> = { major: 0, minor: 1, none: 2, deferred: 3 };
function byDrift(a: PhasePayload, b: PhasePayload): number {
  return (DRIFT_ORDER[a.drift] ?? 99) - (DRIFT_ORDER[b.drift] ?? 99);
}
```

### Verification Sort Order

[VERIFIED: 10-UI-SPEC.md — "Sort order: By phase number ascending"]

```typescript
// Simple ascending sort by phase number:
[...phases].sort((a, b) => a.number - b.number)
```

### No-Project Guard Pattern

[VERIFIED: frontend/src/pages/DashboardPage.tsx line 99 — loading/no-project guards]
[VERIFIED: 10-UI-SPEC.md — identical no-project copy for all three pages]

```tsx
// All three pages open with:
if (loading) return <div className="p-6 text-[#858585] text-sm">Loading…</div>;
if (!activeProject)
  return <div className="p-6 text-[#858585] text-sm">Add scan roots in Settings and select a project.</div>;
```

Note: UI-SPEC uses `p-6` (not `p-8` which the current stubs use). Use `p-6` to match the established pattern.

### Markdown Render Pattern

[VERIFIED: frontend/src/pages/DashboardPage.tsx lines 189-209 — ReactMarkdown with prose classes]

```tsx
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

<div className="prose prose-invert prose-sm max-w-none">
  <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
</div>
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Date formatting | Custom date util | `fmtDate()` (extract to utils.ts) | Already used across the app; consistent output |
| Drift age calculation | Custom date math | `planAgeDays()` helper — 1 line using `Date.now()` minus parsed ISO string | Simple enough to inline; do not reach for a date library |
| Markdown rendering | Custom markdown parser | `ReactMarkdown + remarkGfm` | Already installed; used in DashboardPage and DocsPage |
| Collapse/expand state | Animated accordion library | `useState<boolean>` + conditional render | App has no animation library; CSS `opacity-60` is the only transition |
| Sort function | lodash orderBy | Inline comparator | Project uses no utility library; sort by drift priority map is 4 lines |

**Key insight:** Every visual primitive needed for this phase already exists in the codebase. The work is composition and wiring, not invention.

---

## Common Pitfalls

### Pitfall 1: Floating `p-8` in Stub Content
**What goes wrong:** The three stubs currently use `p-8` (`<div className="p-8 text-[#858585]">`). The UI-SPEC specifies `p-6` for all three pages.
**Why it happens:** Stub content is placeholder; spec uses established `p-6` container standard.
**How to avoid:** Replace the entire stub with the real implementation. Do not patch around the old padding.
**Warning signs:** If a no-project guard renders with `p-8` after implementation, the stub wrapper was not fully replaced.

### Pitfall 2: `plan_write_time` Missing from TypeScript
**What goes wrong:** DriftPage accesses `phase.plan_write_time` but TypeScript reports a type error because the field is absent from `PhasePayload`.
**Why it happens:** The field was added to Pydantic `PhaseEntry` in Phase 9 and serializes correctly in the API response, but the TypeScript interface was not updated.
**How to avoid:** Add `plan_write_time?: string | null` to `PhasePayload` in `api.ts` as an explicit prerequisite task.
**Warning signs:** `tsc -b` fails with "Property 'plan_write_time' does not exist on type 'PhasePayload'".

### Pitfall 3: Unused Import / Parameter TypeScript Errors
**What goes wrong:** `tsc` fails with `noUnusedLocals` or `noUnusedParameters` violations when stubbing out pages.
**Why it happens:** Project `tsconfig.json` enforces these strictly.
**How to avoid:** Only import what is used. Do not leave placeholder imports.
**Warning signs:** Pre-commit or build step shows TS2304 or TS6133.

### Pitfall 4: `has_validation=false` Rows Treated as Clickable
**What goes wrong:** Clicking a phase row with no validation file causes an expand/collapse toggle on an empty string, rendering nothing or throwing.
**Why it happens:** Expand handler wired unconditionally to all rows.
**How to avoid:** Guard the click handler: only rows with `has_validation === true` are expandable. Use `<div>` not `<button>` for non-expandable rows (per UI-SPEC Accessibility section).
**Warning signs:** Clicking a "None" validation row causes the expand indicator to flip.

### Pitfall 5: Sort Mutation
**What goes wrong:** `phases.sort(byDrift)` mutates the array from `useMemo`, which can cause unexpected re-renders or stale data if the array reference is shared.
**Why it happens:** JavaScript `Array.sort()` mutates in place.
**How to avoid:** Always `[...phases].sort(...)` — spread before sorting.
**Warning signs:** DashboardPage phase list reorders unexpectedly when DriftPage is visited.

### Pitfall 6: DashboardPage Import Break After Utils Extraction
**What goes wrong:** After moving `fmtDate`, `statusLabel`, `byLastUpdated`, `statusBorderClass` to `utils.ts`, `DashboardPage.tsx` still has the old local definitions, causing duplicate identifier errors or stale behavior.
**Why it happens:** Extraction task updates `utils.ts` but forgets to update the import in `DashboardPage.tsx`.
**How to avoid:** The utils extraction task must: (a) create `utils.ts`, (b) remove the definitions from `DashboardPage.tsx`, (c) add the import.
**Warning signs:** TypeScript reports duplicate function declarations, or `fmtDate` in DashboardPage uses a different code path than in new pages.

### Pitfall 7: QuickTasks planningPath vs quickPlanningRoot
**What goes wrong:** The `fetchQuickTasks` API expects the `.planning/` root path, but the caller accidentally passes `activeSegment.repoRoot` or `activeSegment.quickPlanningRoot`.
**Why it happens:** `SegmentPayload` has both `planningPath` and `quickPlanningRoot`. `QuickTaskParser.parse()` in Python uses the path directly and looks for `{path}/quick/`.
**How to avoid:** QTSK-01 states "fetches from the existing `/api/quick-tasks/{planningPath}` endpoint" — use `activeSegment.planningPath`.
**Warning signs:** 404 from the API, or an empty task list on a project that has quick tasks.

---

## Code Examples

### DriftPage Skeleton

```tsx
// Source: 10-UI-SPEC.md DriftPage interaction contract
import { useMemo, useState } from "react";
import { useApp } from "../context";
import { fmtDate, statusLabel, statusBorderClass } from "../utils";

export function DriftPage() {
  const { activeProject, loading } = useApp();
  const [showDeferred, setShowDeferred] = useState(false);

  const allPhases = useMemo(
    () => activeProject?.milestones.flatMap((m) => m.phases) ?? [],
    [activeProject],
  );

  const DRIFT_ORDER: Record<string, number> = { major: 0, minor: 1, none: 2, deferred: 3 };
  const activePhases = useMemo(
    () =>
      [...allPhases]
        .filter((p) => !(p.status === "not_started" && p.drift === "deferred"))
        .sort((a, b) => (DRIFT_ORDER[a.drift] ?? 99) - (DRIFT_ORDER[b.drift] ?? 99)),
    [allPhases],
  );
  const deferredPhases = useMemo(
    () => allPhases.filter((p) => p.status === "not_started" && p.drift === "deferred"),
    [allPhases],
  );

  if (loading) return <div className="p-6 text-[#858585] text-sm">Loading…</div>;
  if (!activeProject)
    return <div className="p-6 text-[#858585] text-sm">Add scan roots in Settings and select a project.</div>;

  return (
    <div className="p-6">
      <div className="space-y-2">
        {activePhases.map((p) => (
          <div
            key={p.number}
            className={`w-full rounded-md border border-[#474747] border-l-[3px] ${statusBorderClass(p.status)} bg-[#1e1e1e] p-4`}
          >
            {/* left: number + title; right: status + drift badge + plan age + last updated */}
          </div>
        ))}
      </div>
      {deferredPhases.length > 0 && (
        <>
          <button
            type="button"
            className="mt-4 flex items-center gap-1 text-xs text-[#858585] hover:text-[#cccccc]"
            onClick={() => setShowDeferred((v) => !v)}
            aria-expanded={showDeferred}
            aria-controls="deferred-phases"
          >
            <span>{showDeferred ? "⌄" : "›"}</span>
            <span>
              {showDeferred
                ? "Hide un-started phases"
                : `Show ${deferredPhases.length} un-started phases`}
            </span>
          </button>
          {showDeferred && (
            <div id="deferred-phases" className="mt-2 space-y-2 opacity-60">
              {deferredPhases.map((p) => (
                <div key={p.number} className="...">
                  {/* same row structure */}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
```

### QuickTasksPage Skeleton

```tsx
// Source: 10-UI-SPEC.md QuickTasksPage interaction contract + frontend/src/api.ts
import { useEffect, useMemo, useState } from "react";
import { useApp } from "../context";
import { fetchQuickTasks } from "../api";
import type { QuickTaskPayload } from "../api";
import { fmtDate } from "../utils";

export function QuickTasksPage() {
  const { activeSegment, loading } = useApp();
  const [tasks, setTasks] = useState<QuickTaskPayload[]>([]);
  const [fetchLoading, setFetchLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeSegment?.planningPath) return;
    setFetchLoading(true);
    void fetchQuickTasks(activeSegment.planningPath)
      .then((t) => { setTasks(t); setError(null); })
      .catch(() => setError("Could not load quick tasks. Check your project path and try refreshing."))
      .finally(() => setFetchLoading(false));
  }, [activeSegment?.planningPath]);

  // Sort by last_updated descending (QTSK-05)
  const sorted = useMemo(
    () =>
      [...tasks].sort((a, b) => {
        if (a.last_updated && b.last_updated)
          return b.last_updated.localeCompare(a.last_updated);
        if (a.last_updated) return -1;
        if (b.last_updated) return 1;
        return 0;
      }),
    [tasks],
  );

  if (loading || fetchLoading) return <div className="p-6 text-[#858585] text-sm">Loading…</div>;
  if (!activeSegment)
    return <div className="p-6 text-[#858585] text-sm">Add scan roots in Settings and select a project.</div>;
  if (error) return <div className="p-6"><p className="text-red-400 text-sm">{error}</p></div>;
  if (sorted.length === 0)
    return (
      <div className="p-6 text-center text-[#858585] text-sm">
        <p className="font-medium">No quick tasks yet</p>
        <p>Quick tasks appear here when you run /gsd:quick in this project.</p>
      </div>
    );

  return (
    <div className="p-6 space-y-2">
      {sorted.map((t) => (
        <div
          key={t.file_path}
          className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4"
        >
          {/* title + status badge + created + last_updated */}
        </div>
      ))}
    </div>
  );
}
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|-----------------|--------|
| DriftPage stub returning placeholder text | Full per-phase drift table | DRFT-02 through DRFT-05 satisfied |
| QuickTasksPage stub | Fetch + render from `/api/quick-tasks/{path}` | QTSK-01 through QTSK-05 satisfied |
| VerificationPage stub | Per-phase table with inline markdown expand | VERIF-01 through VERIF-04 satisfied |
| `plan_write_time` absent from TypeScript | Add `plan_write_time?: string | null` to `PhasePayload` | Unblocks plan-age display in DriftPage |
| `fmtDate`, `statusLabel` etc. defined in DashboardPage | Move to `src/utils.ts` | Shared across all pages without duplication |

---

## Open Implementation Notes

### Note 1: plan_write_time Option A vs Option B

The UI-SPEC flags this as a planner decision. Research confirms:

- **Option A (recommended):** Add `plan_write_time?: string | null` to `PhasePayload` in `api.ts`. Zero backend changes. The field is already serialized. One-line TypeScript addition. DriftPage then computes `planAgeDays(p.plan_write_time)` from the ISO string.
- **Option B:** Show "—" for plan age always and skip the `plan_write_time` field. Meets DRFT-03 minimally but provides less value.

**Recommendation: Option A.** The field is already in the response. The cost is one line in `api.ts`.

### Note 2: Utils Extraction is a Prerequisite

The four helpers (`fmtDate`, `statusLabel`, `byLastUpdated`, `statusBorderClass`) must be in `src/utils.ts` before tasks that implement the new pages begin. This is a hard sequencing constraint because:
1. TypeScript strict mode forbids unused locals — if DashboardPage keeps the originals AND imports from utils, it will have duplicate identifiers.
2. All three new pages need the same helpers — without extraction, each page would re-define them (code duplication, violation of project conventions).

### Note 3: QuickTasksPage Uses activeSegment Not activeProject

DriftPage and VerificationPage read from `activeProject` (available through context). QuickTasksPage uses `activeSegment?.planningPath` to call the fetch API. The no-project guard must check `activeSegment` (not `activeProject`) since that's the dependency for the fetch.

### Note 4: Empty State for DriftPage

If `activePhases.length === 0` AND `deferredPhases.length > 0`, the page shows only the "Show N un-started phases" toggle immediately (no empty content above it). If both are empty (project with zero phases), show: "No drift data — all phases are on track or not yet started." This is an edge case but should be handled.

### Note 5: Verification Expand State Reset

When `activeSegment` changes, `expandedPhase` should reset to `null` to avoid showing stale content from the previous project. This needs a `useEffect(() => setExpandedPhase(null), [activeSegment?.planningPath])`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `plan_write_time` is serialized in the API JSON response today (not just in the Pydantic model) | Note 1, DRFT-03 | If Pydantic excludes `None` fields by default, the field may be absent from some phase responses. Risk: LOW — verified that `model_dump_json()` includes all fields including None values in Pydantic v2 by default. [ASSUMED for Pydantic v2 default serialization behavior; verified by reading the code path in app.py] |
| A2 | Tailwind `bg-red-900/40`, `bg-yellow-900/40`, `bg-green-900/40` with opacity modifier are supported in Tailwind CSS v4 | Badge color section | If v4 changed opacity modifier syntax, badge colors break. Risk: LOW — v4 retains `/opacity` modifier syntax. [ASSUMED based on training knowledge; not verified against v4 changelog] |

**If A1 is wrong:** Add `mode="json"` to `model_dump_json()` call or set `exclude_none=False` explicitly. The current code already uses `mode="json"` on quick tasks: `t.model_dump(mode="json")`.

---

## Environment Availability

Step 2.6: SKIPPED — Phase 10 is a pure frontend code change. All required tools (Node.js, npm, TypeScript compiler, Vite) were confirmed operational in earlier phases. No new external services or CLI tools are introduced.

---

## Sources

### Primary (HIGH confidence — verified by direct codebase inspection)

- `frontend/src/api.ts` — PhasePayload interface, QuickTaskPayload, fetchQuickTasks confirmed
- `frontend/src/pages/DashboardPage.tsx` — fmtDate, statusLabel, byLastUpdated, statusBorderClass, badge pattern, ReactMarkdown pattern
- `frontend/src/pages/DocsPage.tsx` — expand/collapse glyph pattern, aria-expanded pattern
- `gsd_monitor/models/core.py` — PhaseEntry.plan_write_time field presence confirmed
- `gsd_monitor/api/app.py` line 138 — `json.loads(seg.project.model_dump_json())` serialization path
- `gsd_monitor/services/project_discovery.py` — plan_write_time population in _enrich_phase and _enrich_gsd2_slice
- `.planning/phases/10-feature-pages/10-UI-SPEC.md` — full visual and interaction contract
- `.planning/REQUIREMENTS.md` — DRFT-02 through VERIF-04 requirement text
- `frontend/src/context.tsx` — context shape: activeProject, activeSegment
- `.planning/config.json` — nyquist_validation: false confirmed (Validation Architecture section omitted)

### Secondary (MEDIUM confidence)

- `gsd_monitor/parsers/quick_task.py` — QuickTask model fields confirmed match QuickTaskPayload interface

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries verified by direct file inspection; no new installs
- Architecture: HIGH — all patterns verified against actual source files; no speculative patterns
- Pitfalls: HIGH — each pitfall grounded in specific code/config evidence
- plan_write_time serialization: HIGH for model presence; MEDIUM for runtime serialization (not tested live)

**Research date:** 2026-04-12
**Valid until:** 2026-05-12 (stable stack; no fast-moving dependencies)
