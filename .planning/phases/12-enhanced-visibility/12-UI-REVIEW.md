# Phase 12 — UI Review

**Audited:** 2026-06-18
**Baseline:** Abstract 6-pillar standards (no UI-SPEC.md)
**Screenshots:** Not captured (no dev server detected on ports 3000, 5173, 8080)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Copy is specific and context-aware; error messages raw (exposes internal API errors verbatim) |
| 2. Visuals | 2/4 | No page heading or breadcrumb — tab bar floats without orientation; accordion expand icon is a bare Unicode caret with no label |
| 3. Color | 2/4 | 36 hardcoded hex literals — no Tailwind token aliases; all six custom hex values used naked throughout |
| 4. Typography | 3/4 | Only two type sizes (text-xs, text-sm); no body/heading size contrast — entire page is small-print |
| 5. Spacing | 3/4 | Consistent Tailwind scale values; no arbitrary px/rem — minor inconsistency between outer p-6 and inner p-4 card padding |
| 6. Experience Design | 3/4 | Loading and error states present; Archives tab silently shows nothing while Requirements/Waves still loading — state bleed between tabs |

**Overall: 16/24**

---

## Top 3 Priority Fixes

1. **Raw API error exposed to user** (InsightsPage.tsx:280, 292) — When the backend fails, the user sees "Error: 404 Not Found" or a Python stack trace fragment. This breaks trust in a tool meant to give developers confidence. Replace with: `<p className="text-sm text-red-400">Could not load insights — check that this project has a REQUIREMENTS.md file.</p>`

2. **No page title or orientation landmark** (InsightsPage.tsx:256) — The Insights page renders a tab bar with zero heading context. A developer landing here has no immediate visual anchor. Add `<h2 className="mb-4 text-base font-semibold text-[#cccccc]">Insights</h2>` before the tab bar, matching DriftPage's established heading pattern.

3. **36 hardcoded hex literals with no token layer** (InsightsPage.tsx, throughout) — Six raw hex values (`#1e1e1e`, `#2a2d2e`, `#474747`, `#4ec994`, `#858585`, `#cccccc`) are repeated naked across 36 occurrences. Any future theme change requires a grep-and-replace. Define Tailwind CSS variables in `index.css` (e.g., `--color-surface`, `--color-border`, `--color-text-muted`) and reference them via `text-[var(--color-text-muted)]` — or add a Tailwind preset mapping these to named tokens so `text-zinc-500` etc. can be used consistently.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)

**WARNING**

Positive: All empty states are specific and actionable.
- Line 56: "No requirements found — REQUIREMENTS.md not present or empty." — correct context.
- Line 110–113: "No multi-wave phases found — all phases have a single-wave execution plan." — accurate, non-generic.
- Line 208–210: "No archived milestones — shipped milestones will appear here once marked as archived." — clear expectation setting.
- Line 252: "Add scan roots in Settings and select a project." — matches existing app convention.

No generic "Submit", "OK", or "Click Here" labels found.

**Finding — BLOCKER-class copy defect:**
- Lines 280 and 292: `Error: {insightsError}` — the raw JavaScript `Error.message` from a failed `fetch()` call is rendered directly. This can be a 404 URL, an HTTP status string, or a network timeout message. Users see implementation detail, not actionable guidance. No UX copy contract governs what this should say.

**Finding — minor:**
- Line 247: `"Loading\u2026"` (global loading guard) is functional but terse. Consistent with other pages, so acceptable at 3/4 rather than a deduction.

---

### Pillar 2: Visuals (2/4)

**WARNING**

**Finding — no page heading:**
The page jumps directly to a tab bar. Every other feature page in the codebase (DriftPage, QuickTasksPage) begins with a heading that names the view. InsightsPage has no `<h1>` or `<h2>`. A user who lands here via direct URL has no visual confirmation they are on the Insights page — the nav link is the only identifier and it scrolls off-screen on shorter viewports.

**Finding — accordion expand/collapse icon is semantically bare:**
- Line 165: `{expanded ? "\u2304" : "\u203A"}` — the expand chevron and right angle quotation mark (`‹`) are Unicode punctuation characters wrapped only in `<span className="text-xs text-[#858585]">`. They carry no `aria-label` on the parent button. The `aria-expanded` attribute (line 161) is correct and provides screen reader state, but the visual affordance is weak — `›` (U+203A) is a right single guillemet, not a standard disclosure triangle. A user seeing `›` beside a title might not recognize it as clickable.

**Finding — no visual differentiation between tabs:**
The active tab uses `bg-[#2a2d2e]` (a single-step background shift from the page background `#1e1e1e`). The contrast delta is minimal. Without screenshots this cannot be scored definitively, but the hex values indicate the active state is barely distinguishable. No border, underline, or accent color is used to mark the active tab. This is a borderline WARNING rather than BLOCKER since keyboard focus would still navigate.

**Finding — Requirements table has no column width constraints:**
The Description column (`td` line 82) receives all remaining table width. With long requirement descriptions and narrow viewports (Edge WebView2 at smaller window sizes), the Phase and Status columns can be squeezed. No `w-` classes or `min-w-` classes are applied to any column. For a desktop tool this is acceptable but notable.

---

### Pillar 3: Color (2/4)

**WARNING**

36 occurrences of hardcoded hex literals in InsightsPage.tsx alone. Six distinct values:

| Hex | Role | Occurrences (approx.) |
|-----|------|----------------------|
| `#cccccc` | Primary text | ~8 |
| `#858585` | Muted / secondary text | ~10 |
| `#474747` | Borders | ~9 |
| `#1e1e1e` | Card background | ~4 |
| `#2a2d2e` | Active state / badge bg | ~4 |
| `#4ec994` | Success green | ~2 |

These are consistent with the rest of the codebase (ShellLayout uses the same values), so there is no color-consistency failure between components. The failure is architectural: the design vocabulary exists but is not codified anywhere as tokens. Every component author must memorize or copy-paste exact hex strings. A typo produces an invisible regression.

**No color overuse issue:** Accent green (`#4ec994`) is used only on Complete status badges — correct application.

**No 60/30/10 distribution failure detected** at the color-role level (neutral grays dominate, green reserved for success state only).

Deducted 2 points rather than 1 because the lack of token layer is a systemic risk across all 12 pages of this app, not just InsightsPage.

---

### Pillar 4: Typography (3/4)

**WARNING (minor)**

Font sizes in use across InsightsPage.tsx:
- `text-xs`: 8 occurrences — badges, category headers, accordion meta text
- `text-sm`: 14 occurrences — body text, table cells, error/loading messages

**Finding — no heading-size text on the page:**
The entire Insights page is rendered at `text-sm` or smaller. There is no `text-base` or larger size used for any heading, page title, or landmark. This makes the page feel flat and dense — all elements are visually equal weight. The category headers compensate via `font-semibold uppercase tracking-wider` (line 64) but remain at `text-xs`, which is visually quieter than the content it headers.

Font weights in use:
- `font-medium`: tab buttons (line 263), accordion title (line 166), wave phase header (line 132), table header (line 70-73)
- `font-semibold`: category header (line 64)
- `font-mono`: ID cell (line 79), wave phase number (line 132), archive phase number (line 181)

Two weights plus mono is a reasonable distribution for a data-dense page. The weight system is internally consistent.

**No over-proliferation:** Only 2 font sizes, 2 weights (+ mono) — well under the 4-size / 2-weight threshold for a flag.

Minor deduction for the absence of any heading-level size creating hierarchy.

---

### Pillar 5: Spacing (3/4)

**WARNING (minor)**

Spacing classes in InsightsPage.tsx:

| Class | Count | Usage |
|-------|-------|-------|
| `px-3` | 9 | Table cells |
| `py-2` | 8 | Table cells |
| `py-0.5` | 3 | Badges |
| `px-1.5` | 3 | Badges |
| `p-6` | 3 | Page wrapper, loading/empty guards |
| `p-4` | 3 | Cards (wave, archive) |
| `space-y-1` | 2 | Phase list rows |
| `gap-3` | 2 | Row flex gap |
| `gap-2` | 2 | Header flex gap |
| `space-y-4` | 1 | Wave card list |
| `space-y-2` | 1 | Archive item list |
| `gap-1` | 1 | Tab bar gap |
| `py-1.5` | 1 | Tab buttons |

All values are on the standard Tailwind 4-unit scale. No arbitrary `[px]` or `[rem]` values found.

**Finding — outer vs inner padding inconsistency:**
The page wrapper uses `p-6` (24px), but accordion expanded content uses `p-4` (16px) with `border-t-0` to visually merge with the header. The outer page content sits 24px from edges; when expanded accordion content renders, its inner padding is 16px — creating a shifted visual rhythm inside accordions vs. outside. This is minor but noticeable in a dense tool.

**Finding — `gap-1` on tab bar is tight:**
The tab bar uses `gap-1` (4px) between pill buttons. Tab labels "Requirements", "Waves", "Archives" are likely close together. Combined with the subtle active-state color, the tab bar may feel cramped at standard font size. `gap-2` would give better affordance.

---

### Pillar 6: Experience Design (3/4)

**WARNING**

**Present and correct:**
- Global loading guard (line 247): shown while context is loading
- `insightsLoading` state (lines 276-278, 288-290): per-tab loading message shown during fetch
- `insightsError` state (lines 279-281, 291-293): error message rendered on failure
- `aria-expanded` on accordion button (line 161): keyboard/screen reader accessible
- Empty states: all three tabs have empty state messages

**Finding — state bleed on tab switch while fetching:**
When the user switches to the "Archives" tab while `insightsLoading` is still true (e.g., slow API), the Archives tab renders immediately without any loading indicator — because it reads from `activeProject.milestones` (context), not from `insightsData`. This is architecturally correct (Archives doesn't need the API call) but creates an inconsistency: Requirements and Waves show a loading spinner, Archives renders fully. A user who switches tabs during load may briefly think the Archives data is stale or that the tab skipped loading.

**Finding — no page-level heading on error:**
The error display (line 280) is `<p className="text-sm text-red-400">Error: {insightsError}</p>` with no heading or icon. A user who has data from a previous segment selection cached in state will see old Requirements data alongside a new error — because `insightsData` is only nulled on fetch start (line 232) after the effect re-runs on segment change, not when the tab itself changes. The sequence: (1) select project A → data loads; (2) select project B → insightsData briefly null, loading fires; (3) if fetch fails, error is shown BUT insightsData is null (correct). This is actually fine — the null check gates rendering. No actual stale-data display occurs.

**Finding — no `aria-label` on accordion toggle button:**
Line 157–161: The `<button>` has `aria-expanded` correctly but no `aria-label` or `aria-controls`. A screen reader will announce the button content (expanded arrow + milestone title) which is functional, but pairing with `aria-controls` pointing to the expanded section would be best practice for a collapsible widget.

**Finding — Archives tab not recoverable on error:**
If `insightsError` is set (API failure), the Archives tab is unaffected and renders correctly from context. However, there is no "Retry" or "Reload" affordance for the Requirements and Waves tabs. The user must navigate away and back, or wait for a WebSocket-triggered reload, to retry. This is a missing interaction for a data-dense page.

---

## Files Audited

- `D:/gsd-monitor-py/frontend/src/pages/InsightsPage.tsx` (303 lines — primary audit target)
- `D:/gsd-monitor-py/frontend/src/ShellLayout.tsx` (nav wiring verification)
- `D:/gsd-monitor-py/frontend/src/App.tsx` (route wiring verification)
- `D:/gsd-monitor-py/frontend/src/api.ts` (not read in full — type interfaces verified via SUMMARY.md)
- `.planning/phases/12-enhanced-visibility/12-01-PLAN.md`
- `.planning/phases/12-enhanced-visibility/12-01-SUMMARY.md`
- `.planning/phases/12-enhanced-visibility/12-02-PLAN.md`
- `.planning/phases/12-enhanced-visibility/12-02-SUMMARY.md`
- `.planning/phases/12-enhanced-visibility/12-CONTEXT.md`

Registry audit: shadcn not initialized — skipped.
