# Phase 10 — UI Review

**Audited:** 2026-04-12
**Baseline:** 10-UI-SPEC.md (approved design contract)
**Screenshots:** Not captured (no dev server running at localhost:3000, 5173, or 8080)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | One spec deviation: empty state padding uses `p-6 text-center` instead of spec-declared `p-8 text-center`; all copy strings exact |
| 2. Visuals | 4/4 | Clear hierarchy on all three pages; expand glyphs correctly positioned; non-clickable rows correctly use `<div>` |
| 3. Color | 4/4 | All 14 badge color combinations match spec; accent `#007acc` used only in statusBorderClass (in_progress/needs_verification border), not on badges |
| 4. Typography | 4/4 | Only `text-xs` and `text-sm` used across all three pages; only `font-medium` weight (plus `font-mono` for phase titles); fully within spec |
| 5. Spacing | 4/4 | Consistent p-6 page padding, p-4 cards, px-1.5 py-0.5 badges, gap-2/gap-3 flex rows; no arbitrary pixel/rem values |
| 6. Experience Design | 4/4 | All four guard states present on each page; QuickTasksPage adds race-condition cancellation; aria attributes on all collapsible controls |

**Overall: 23/24**

---

## Top 3 Priority Fixes

1. **QuickTasksPage empty state padding does not match spec** — Users who run the app with no quick tasks see a layout that differs from the design contract: `p-6` is used but spec declares `p-8` (`text-center p-8 text-[#858585] text-sm`). This is a minor visual gap but breaks the contract — fix: change `"p-6 text-center text-[#858585] text-sm"` to `"p-8 text-center text-[#858585] text-sm"` at `QuickTasksPage.tsx:83`.

2. **DriftPage empty-state condition is narrower than spec** — Spec says: "No drift data — all phases are on track or not yet started." should show when there is no actionable drift AND no deferred phases. The implementation introduces `hasActionableDrift` as a computed sentinel (`activePhases.some(p => drift === "major" || drift === "minor")`) which means a project where all active phases have `drift === "none"` would render those "none" rows instead of the empty message — even though they represent no meaningful drift signal. Spec intent (DRFT-02 context) is that NONE-drift phases appear in the main list, so this is actually correct behavior, but the empty message copy check would benefit from a comment clarifying the intent for future maintainers. No code fix required — annotate with a comment.

3. **VerificationPage validated-row `aria-expanded` missing `aria-controls`** — The `<button>` for each validated phase row at `VerificationPage.tsx:81` sets `aria-expanded={expandedPhase === p.number}` but has no `aria-controls` attribute pointing to the expanded content `<div>`. Spec Accessibility section requires `aria-controls` on all expand triggers. The collapsible "without validation" button correctly sets `aria-controls="unvalidated-phases"` (line 131), but the per-row expand button does not. Fix: add `aria-controls={`phase-${p.number}-content`}` to the button and `id={`phase-${p.number}-content`}` to the expanded `<div>`.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)

All spec-declared copy strings are implemented exactly:

| Element | Spec | Implemented | Match |
|---------|------|-------------|-------|
| DriftPage empty | "No drift data — all phases are on track or not yet started." | Exact | Pass |
| DriftPage toggle (collapsed) | "Show N un-started phases" | Exact | Pass |
| DriftPage toggle (expanded) | "Hide un-started phases" | Exact | Pass |
| QuickTasksPage empty heading | "No quick tasks yet" | Exact | Pass |
| QuickTasksPage empty body | "Quick tasks appear here when you run /gsd:quick in this project." | Exact | Pass |
| QuickTasksPage load error | "Could not load quick tasks. Check your project path and try refreshing." | Exact | Pass |
| VerificationPage VERIF-04 toggle (collapsed) | "Show N phases without validation" | Exact | Pass |
| VerificationPage VERIF-04 toggle (expanded) | "Hide phases without validation" | Exact | Pass |
| VerificationPage empty | "No phases found for this project." | Exact | Pass |
| No-project state (all pages) | "Add scan roots in Settings and select a project." | Exact | Pass |
| Loading state (all pages) | "Loading…" | Exact (unicode `\u2026` or direct `…`) | Pass |
| Plan age display | "N days" / "1 day" / "—" | Exact (singular handled at DriftPage.tsx:54) | Pass |
| Drift badge labels | "Major" / "Minor" / "None" / "Deferred" | Exact | Pass |
| Quick task status labels | "Open" / "In progress" / "Complete" | Exact | Pass |
| Verification has_validation labels | "Validated" / "None" | Exact | Pass |
| Verification nyquist labels | "Pass" / "Fail" / "Unknown" | Exact | Pass |
| Verification has_uat labels | "UAT" / "No UAT" | Exact | Pass |

**One deviation found:** `QuickTasksPage.tsx:83` — the empty-state container uses `"p-6 text-center text-[#858585] text-sm"` but the spec (UI-SPEC.md, QuickTasksPage section) declares `"text-center p-8 text-[#858585] text-sm"`. The padding token is `p-6` (24px) instead of `p-8` (32px). All other strings within the block are correct.

No generic labels (Submit, OK, Cancel, Save) found. No "No results" / "No data" generic patterns used.

---

### Pillar 2: Visuals (4/4)

**DriftPage:** Clear focal point — phase title and drift badge at opposite ends of each row. MAJOR badges draw the eye first due to red color. Deferred section correctly hidden, providing a clean default state. The `PhaseCard` sub-component extraction (from the code-review fix in 10-VERIFICATION.md) eliminates duplicated markup and is a visual correctness improvement — both active and deferred cards render identically.

**QuickTasksPage:** Tasks sorted most-recent-first, matching user mental model. Status badge on the right provides quick status scan. `title` attributes on the two date spans (`Created`, `Last updated`) provide tooltip differentiation for the two visually similar date values — a positive addition not required by spec.

**VerificationPage:** Expand glyph (`›` / `⌄`) positioned left of phase number per spec. Unvalidated section at `opacity-60` creates appropriate visual de-emphasis. `<button>` vs `<div>` distinction correctly applied: validated rows are buttons; unvalidated rows in the collapsed section are divs. The `{" "}` spacer at VerificationPage.tsx:149 preserves column alignment for unvalidated rows (glyph column shows a space, not a glyph).

**No icon-only buttons found.** All toggle controls include text labels alongside glyphs.

---

### Pillar 3: Color (4/4)

All 14 semantic badge color combinations verified against spec:

**Drift badges (DriftPage.tsx:6-16):**
- MAJOR: `bg-red-900/40 text-red-400` — matches spec
- MINOR: `bg-yellow-900/40 text-yellow-400` — matches spec
- NONE: `bg-green-900/40 text-[#4ec994]` — matches spec
- DEFERRED (default): `bg-[#2a2d2e] text-[#858585]` — matches spec

**Quick task badges (QuickTasksPage.tsx:7-16):**
- open (default): `bg-[#2a2d2e] text-[#858585]` — matches spec
- in_progress: `bg-yellow-900/40 text-yellow-400` — matches spec
- complete: `bg-green-900/40 text-[#4ec994]` — matches spec

**Verification badges (VerificationPage.tsx:7-29):**
- has_validation=true: `bg-green-900/40 text-[#4ec994]` — matches spec
- has_validation=false: `bg-[#2a2d2e] text-[#858585]` — matches spec
- nyquist=true: `bg-green-900/40 text-[#4ec994]` — matches spec
- nyquist=false: `bg-red-900/40 text-red-400` — matches spec
- nyquist=null: `bg-[#2a2d2e] text-[#858585]` — matches spec
- has_uat=true: `bg-green-900/40 text-[#4ec994]` — matches spec
- has_uat=false: `bg-[#2a2d2e] text-[#858585]` — matches spec

**Accent color (`#007acc`):** Correctly reserved for status border stripes on in_progress/needs_verification phases via `statusBorderClass`. Not used for badge backgrounds or text on any new page. No `text-primary` or `bg-primary` utility classes present.

**Hardcoded colors:** All instances of `#RRGGBB` values in the new files are from the spec-declared design token set (`#1e1e1e`, `#2a2d2e`, `#474747`, `#cccccc`, `#858585`, `#4ec994`, `#007acc`). No off-palette colors introduced.

---

### Pillar 4: Typography (4/4)

Font size distribution across all three new pages + utils.ts:
- `text-xs` — 12px, used for badges, secondary labels, dates, toggle buttons
- `text-sm` — 14px, used for primary row text, loading/error/empty states

No `text-base`, `text-lg`, `text-xl`, `text-2xl`, `text-3xl` or larger classes appear on any of the three feature pages. Spec explicitly prohibits text-lg, text-xl, text-3xl on data pages — contract met.

Font weight distribution:
- `font-medium` — used for badge text, phase titles
- `font-mono` — used for phase number+title display (not a weight, a family modifier)

No `font-bold`, `font-semibold`, or `font-light` appears on the new pages. Spec allows `font-medium` for section headings and metrics. The `font-semibold` used in ShellLayout (`GSD Monitor` app title) is a pre-existing pattern not introduced in this phase.

Phase title pattern `font-mono font-medium text-[#cccccc]` correctly applied across all three pages per spec declaration.

---

### Pillar 5: Spacing (4/4)

Spacing token usage observed (all values are Tailwind scale multiples of 4px):

| Class | px Value | Usage |
|-------|----------|-------|
| `p-6` | 24px | Page container (all three pages) — matches spec `lg` token |
| `p-4` | 16px | Card/row padding — matches spec `md` token |
| `px-1.5 py-0.5` | 6px/2px | Badge inner padding — matches spec `xs` token |
| `space-y-2` | 8px | Row gap in lists — matches spec `sm` token |
| `gap-2` | 8px | Flex row gap (badge cluster) |
| `gap-3` | 12px | Flex row gap (DriftPage right-side metadata cluster) |
| `gap-1` | 4px | Toggle button glyph+text gap |
| `mt-4` | 16px | Deferred/unvalidated toggle top margin |
| `mt-2` | 8px | Expanded section top margin |

No arbitrary spacing values (`[N px]` or `[N rem]`) introduced in these pages beyond the spec-approved `border-l-[3px]` (established pattern from DashboardPage, explicitly called out in spec Exceptions table).

The `p-8` value is absent from all three pages — spec correctly declares p-8 as stub-only padding and all three pages replaced their stubs. The one discrepancy is the QuickTasksPage empty state using `p-6` where spec says `p-8` — documented in Pillar 1.

---

### Pillar 6: Experience Design (4/4)

**State coverage per page:**

| State | DriftPage | QuickTasksPage | VerificationPage |
|-------|-----------|----------------|------------------|
| Loading | `p-6 text-[#858585] text-sm` guard | Dual guard (`loading \|\| fetchLoading`) | `p-6 text-[#858585] text-sm` guard |
| No-project | "Add scan roots…" guard | "Add scan roots…" guard (no-segment) | "Add scan roots…" guard |
| Error | not applicable (context data) | Red `text-red-400` message | not applicable (context data) |
| Empty | "No drift data…" message | "No quick tasks yet" with body | "No phases found…" guard |
| Data | Phase rows, badges, collapsible deferred | Task rows, badges, dates | Phase rows, badges, expandable content |

**QuickTasksPage adds cancellation pattern** (not required by spec): `let cancelled = true` in useEffect cleanup prevents state updates after component unmounts or segment changes. This is a positive experience improvement — prevents stale data flicker.

**Collapsible sections:** Both DriftPage (deferred phases) and VerificationPage (unvalidated phases) implement `aria-expanded` on toggle buttons. DriftPage at DriftPage.tsx:111-112 and VerificationPage at VerificationPage.tsx:130-131 both include correct `aria-controls` pointing to the container `id`.

**Gap identified:** VerificationPage per-row expand buttons (`button` at VerificationPage.tsx:75-110) have `aria-expanded` but no `aria-controls`. Screen readers can understand the expanded state but cannot programmatically navigate to the expanded content. The spec accessibility section requires `aria-controls` on all expand triggers.

**No destructive actions** exist on any of the three pages. Confirmation dialogs are correctly absent. The app remains read-only throughout.

**Reset behavior:** VerificationPage correctly resets `expandedPhase` to null on `activeSegment?.planningPath` change (VerificationPage.tsx:36-38), preventing stale expanded content when the user switches projects.

---

## Registry Safety

No `components.json` found — shadcn not initialized. No third-party component registries used. All three pages rely exclusively on existing project dependencies (`react-markdown`, `remark-gfm`, Tailwind CSS). Registry audit skipped per protocol.

---

## Files Audited

- `D:\gsd-monitor-py\frontend\src\pages\DriftPage.tsx`
- `D:\gsd-monitor-py\frontend\src\pages\QuickTasksPage.tsx`
- `D:\gsd-monitor-py\frontend\src\pages\VerificationPage.tsx`
- `D:\gsd-monitor-py\frontend\src\utils.ts`
- `D:\gsd-monitor-py\frontend\src\ShellLayout.tsx` (nav registration verification)
- `D:\gsd-monitor-py\.planning\phases\10-feature-pages\10-UI-SPEC.md` (audit baseline)
- `D:\gsd-monitor-py\.planning\phases\10-feature-pages\10-01-SUMMARY.md`
- `D:\gsd-monitor-py\.planning\phases\10-feature-pages\10-02-SUMMARY.md`
- `D:\gsd-monitor-py\.planning\phases\10-feature-pages\10-03-SUMMARY.md`
