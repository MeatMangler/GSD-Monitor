---
phase: 10-feature-pages
status: advisory
reviewed: 2026-04-12
depth: standard
files_reviewed: 6
files_reviewed_list:
  - frontend/src/utils.ts
  - frontend/src/api.ts
  - frontend/src/pages/DashboardPage.tsx
  - frontend/src/pages/DriftPage.tsx
  - frontend/src/pages/QuickTasksPage.tsx
  - frontend/src/pages/VerificationPage.tsx
---

# Phase 10: Code Review Report

**Reviewed:** 2026-04-12
**Depth:** standard
**Files Reviewed:** 6
**Status:** advisory — no blocking bugs or security issues; several warning-level concerns worth fixing before shipping

## Summary

The Phase 10 additions (three new feature pages plus shared utilities) are structurally sound and follow established project conventions. Component decomposition, hook usage, and TypeScript typing are consistent with the existing codebase. The new `utils.ts` module is a clean, well-scoped extraction.

The primary concern area is **ReactMarkdown usage**: `plan_content`, `research_content`, and `validation_content` are rendered without HTML stripping. React-markdown v10's `defaultUrlTransform` does block `javascript:` links, but inline HTML in the markdown source is passed through as raw text nodes (not executed), so XSS is not a live risk at this point. However, if `rehype-raw` is ever added, the absence of `rehype-sanitize` would immediately open an XSS vector — the current pattern warrants a defensive hardening note.

Three logic-level warnings also need attention: a stale `fmtDate(t.created)` column that adds noise, a missing stale-fetch guard in `QuickTasksPage`, and minor display ambiguity in the DriftPage "empty" condition.

---

## Warnings

### WR-01: Missing stale-fetch guard in QuickTasksPage useEffect

**File:** `frontend/src/pages/QuickTasksPage.tsx:35-49`

**Issue:** The `useEffect` that fetches quick tasks has no cleanup/cancellation. If `activeSegment.planningPath` changes while a fetch is in flight (e.g., user switches projects rapidly), `setTasks` and `setError` will update state for the wrong segment. The effect runs the async call fire-and-forget with `void`, so the stale setter calls land on the component for the newly-selected project.

**Fix:** Return a cleanup function that sets an `isCancelled` flag, or use `AbortController`:

```ts
useEffect(() => {
  if (!activeSegment?.planningPath) return;
  let cancelled = false;
  setFetchLoading(true);
  fetchQuickTasks(activeSegment.planningPath)
    .then((t) => {
      if (!cancelled) { setTasks(t); setError(null); }
    })
    .catch(() => {
      if (!cancelled)
        setError("Could not load quick tasks. Check your project path and try refreshing.");
    })
    .finally(() => { if (!cancelled) setFetchLoading(false); });
  return () => { cancelled = true; };
}, [activeSegment?.planningPath]);
```

---

### WR-02: DriftPage "no data" condition incorrectly hides phases with no drift information

**File:** `frontend/src/pages/DriftPage.tsx:66-68`

**Issue:** The empty-state branch fires only when both `activePhases` and `deferredPhases` are empty. `activePhases` is built by filtering out phases where `status === "not_started" && drift === "deferred"`. But phases with `status === "not_started"` and `drift === "none"` are included in `activePhases` even though they carry no actionable drift signal. On a fresh project with all phases not-started and drift=none, the page renders a list of green "None" badges with no context. The empty-state message ("No drift data — all phases are on track") is more informative but never shown in this case.

**Fix:** Expand the empty-state condition to also treat all-`none`-drift phases as "on track":

```ts
const hasActionableDrift = activePhases.some(
  (p) => p.drift === "major" || p.drift === "minor"
);

// then:
{!hasActionableDrift && deferredPhases.length === 0 ? (
  <p className="text-[#858585] text-sm">
    No drift data — all phases are on track or not yet started.
  </p>
) : ( ... )}
```

---

### WR-03: DriftPage phase card rendering duplicated verbatim

**File:** `frontend/src/pages/DriftPage.tsx:71-95` and `113-138`

**Issue:** The phase card markup (border classes, status label, drift badge, plan age, last-updated date) is copy-pasted identically between the `activePhases` list and the `deferredPhases` list inside `showDeferred`. This is a direct maintenance hazard: a future field addition will require two edits with no compiler enforcement.

**Fix:** Extract a `PhaseCard` sub-component:

```tsx
function PhaseCard({ p }: { p: PhasePayload }) {
  return (
    <div className={`w-full rounded-md border border-[#474747] border-l-[3px] ${statusBorderClass(p.status)} bg-[#1e1e1e] p-4`}>
      {/* shared card body */}
    </div>
  );
}
```

This brings the file in line with the single-responsibility convention described in CLAUDE.md.

---

### WR-04: `fmtDate(t.created)` column always shows "—" for directory-based tasks

**File:** `frontend/src/pages/QuickTasksPage.tsx:105`

**Issue:** `QuickTaskPayload.created` is populated from `st_ctime` (creation time). On Windows, `st_ctime` is genuinely the file creation timestamp, so this is accurate for freshly created quick tasks. However, the `QuickTaskParser` uses `rep.stat().st_ctime` where `rep` is the `PLAN.md` representative file — not the directory itself. When a PLAN.md is regenerated (e.g., amended by the quick workflow), `ctime` updates and no longer reflects when the task was created. The label "Created" would therefore be misleading. The column currently has no label at all in the rendered UI (it's the second date column, silently adjacent to `last_updated`), making the two identical-looking date spans confusing.

**Fix (minimal):** Add a `title` attribute to distinguish the two date spans:

```tsx
<span className="text-xs text-[#858585]" title="Created">
  {fmtDate(t.created)}
</span>
<span className="text-xs text-[#858585]" title="Last updated">
  {fmtDate(t.last_updated)}
</span>
```

Or remove the created column entirely if the backend can't guarantee its accuracy — `last_updated` is sufficient for the default sort.

---

## Info

### IN-01: ReactMarkdown renders without explicit `skipHtml` — document intent

**File:** `frontend/src/pages/DashboardPage.tsx:151,159,167`, `frontend/src/pages/VerificationPage.tsx:114`

**Issue:** `<ReactMarkdown>` is used without `skipHtml` in all four invocations. React-markdown v10 (without `rehype-raw`) does not parse or execute raw HTML in the source — inline HTML tags are emitted as escaped text nodes, not DOM elements. Combined with `defaultUrlTransform` (which rejects `javascript:` and `data:` links), there is **no live XSS risk** in the current configuration.

However, the safe behaviour depends on the absence of `rehype-raw` from the plugin chain. If `rehype-raw` is added in the future (a common requirement for GFM tables with HTML cells), the sanitization gap would become exploitable. This risk is elevated because the markdown content comes from files on disk that developers can author — including any HTML they choose.

**Recommendation:** Add `skipHtml` to each invocation as a defensive default, and add a comment explaining the decision so it is not accidentally dropped:

```tsx
{/* skipHtml: block raw HTML passthrough — safe default; add rehype-sanitize before removing */}
<ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml>
  {selected.plan_content}
</ReactMarkdown>
```

This is a hardening step, not an urgent bug fix.

---

### IN-02: `byLastUpdated` sort comparator used on `PhasePayload` but `PhasePayload.number` is not guaranteed unique across milestones

**File:** `frontend/src/utils.ts:1-9`, `frontend/src/pages/DashboardPage.tsx:13-19`

**Issue:** `byLastUpdated` uses `b.number - a.number` as a tiebreaker. In DashboardPage, phases from all milestones are flattened and sorted together. Phase numbers are unique within a milestone but are not guaranteed globally unique across milestones (milestone 1 phase 1 and milestone 2 phase 1 both have `number === 1`). The key used for the list items — `` `${p.number}-${p.title}` `` (line 118) — partially accounts for this by including the title, but the sort tiebreaker can produce non-deterministic ordering when two phases from different milestones share the same number and both lack `last_updated`.

**Fix:** Use a compound tiebreaker in `byLastUpdated`, or flatten with a `milestoneIndex` attached:

```ts
// In DashboardPage, add milestone index to each phase before sorting
.flatMap((m, mi) => m.phases.map((p) => ({ ...p, milestoneTitle: m.title, milestoneIndex: mi })))
.sort((a, b) => {
  // ... existing date comparator ...
  if (a.number !== b.number) return b.number - a.number;
  return b.milestoneIndex - a.milestoneIndex; // stable tiebreaker
})
```

---

### IN-03: `fmtDate` uses the browser locale `en-US` unconditionally

**File:** `frontend/src/utils.ts:12-14`

**Issue:** `toLocaleDateString("en-US", ...)` hardcodes locale regardless of the user's system locale. This is inconsistent with a Windows desktop app where the OS locale is authoritative. On a system set to a non-US locale the date format will still display in US order (e.g., "Apr 12, 2026").

**Fix:** Use `undefined` (system locale) or make it configurable:

```ts
export function fmtDate(d: string | null | undefined): string {
  if (!d) return "—";
  return new Date(d).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}
```

---

### IN-04: `statusBorderClass` applied to `not_started` phases renders the "deferred" border as neutral grey — "deferred" drift phases are visually indistinguishable

**File:** `frontend/src/utils.ts:29-38`, `frontend/src/pages/DriftPage.tsx:74,116`

**Issue:** `statusBorderClass` returns `border-l-[#474747]` (neutral grey) for any status that isn't `complete`, `in_progress`, or `needs_verification`. Deferred/not-started phases therefore get the same grey border as generic "no status" entries, even on the Drift page where drift severity is the primary signal. A user scanning the list must read the drift badge rather than using the border as a pre-attentive visual anchor.

This is a design observation, not a correctness bug. No fix required if the intent is to keep the border tied to phase status only.

---

### IN-05: Magic string `"not_started"` checked inline in DriftPage rather than via `statusLabel`

**File:** `frontend/src/pages/DriftPage.tsx:50,56`

**Issue:** The filter `p.status === "not_started"` is spelled out inline. The `statusLabel` utility (which maps `"not_started"` → `"Not started"`) already knows about this string. If the backend renames the status value, the filter and the label would drift. Minor consistency concern.

**Fix:** Define a typed union or enum for phase status strings in `api.ts` and import it:

```ts
export type PhaseStatus = "complete" | "in_progress" | "needs_verification" | "not_started";
```

Then annotate `PhasePayload.status` with `PhaseStatus` instead of `string`.

---

### IN-06: VerificationPage `useEffect` reset fires on every `activeSegment` object change, not just `planningPath`

**File:** `frontend/src/pages/VerificationPage.tsx:36-38`

**Issue:** `useEffect(() => { setExpandedPhase(null); }, [activeSegment?.planningPath])` correctly resets the expanded phase when the project changes. This is well-scoped. However, if `activeSegment` is reconstructed by `useMemo` in `context.tsx` on every render (which it is — `useMemo` returns a new object reference when `activeGroup` or `selectedSegmentKey` changes), the `?.planningPath` optional chaining correctly collapses to a primitive string for dep comparison, so the effect is not over-fired. This is correct as written.

No change required — this note is for reviewer awareness only.

---

_Reviewed: 2026-04-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
