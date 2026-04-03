# Phase 2: Visual Redesign - Research

**Researched:** 2026-04-03
**Domain:** React 19 / Tailwind CSS v4 / TypeScript — frontend-only UI reskin
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Replace stats grid card 1: `% completion` (unchanged)
- **D-02:** Replace stats grid card 2: `phases done/total` (replaces milestones count)
- **D-03:** Replace stats grid card 3: `active phase name` — title of first `in_progress` phase (replaces active phases count)
- **D-04:** Drift label stays as the 4th card — do not remove it
- **D-05:** Keep the 4-card grid layout; do not switch to a horizontal bar
- **D-06:** Each phase row gets a colored left border: green (`#4ec994`) for `complete`, blue (`#007acc`) for `in_progress`, gray (`#474747`) for `not_started`
- **D-07:** Keep the current recency sort (`last_updated` descending) — do not switch to numeric order
- **D-08:** Keep the drawer — clicking a phase still opens plan/research/validation content
- **D-09:** Breadcrumb lives at the top of DashboardPage content area, above the stats cards — not in ShellLayout
- **D-10:** Segments: `group.displayName` → `activeProject.name` → title of the first `in_progress` phase
- **D-11:** If no `in_progress` phase exists, show the last `complete` phase or `—`
- **D-12:** Active phase is derived from phase list status data; StateParser wiring is a Phase 4 concern — do not block on it
- **D-13:** Use exact VS Code Dark+ hex tokens: editor bg `#1e1e1e`, sidebar bg `#252526`, hover `#2a2d2e`, borders `#474747`, accent blue `#007acc`, primary text `#cccccc`, muted text `#858585`
- **D-14:** Set `font-family: "Segoe UI", system-ui, sans-serif` in `index.css` at body level
- **D-15:** Phase numbers and code snippets continue to use a monospace font stack (`"Cascadia Code", "Consolas", monospace`)

### Claude's Discretion

- Status label text format — keep consistent with current `statusLabel()` function
- Exact border width for colored left border (2–4px; 3px chosen in UI-SPEC)
- Whether breadcrumb segments are truncated with ellipsis when long (truncate on terminal segment with `max-w-[240px]`)
- Exact shade of green/gray (use VS Code terminal green `#4ec994`)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DASH-01 | Stats bar visible immediately above the fold: % complete, phases done/total, active phase name | Stats `useMemo` extension pattern; all data available in `activeProject.milestones[].phases[]` |
| DASH-02 | Phase list shows all phases with status colors (done=green, active=blue, todo=gray) without any click required | Tailwind v4 arbitrary value `border-l-[3px] border-l-[#4ec994]` pattern confirmed; left-border approach verified in UI-SPEC |
| DASH-03 | Breadcrumb always visible: repo name → project name → active phase | `useApp()` exposes `groups`, `activeSegment`, `activeProject` — all breadcrumb segments derivable without context changes |
| DASH-04 | UI uses VS Code dark theme: dark background (#1e1e1e range), sidebar, matching typography and contrast | Token swap table fully documented in UI-SPEC; Tailwind v4 arbitrary values confirmed as the correct mechanism |
</phase_requirements>

---

## Summary

This phase is a pure frontend reskin — no backend changes, no new components, no new pages. Three files are touched: `frontend/src/index.css` (font family), `frontend/src/pages/DashboardPage.tsx` (stats bar content + breadcrumb + phase row classes), and `frontend/src/ShellLayout.tsx` (color token swaps). The UI-SPEC document (`02-UI-SPEC.md`) is the authoritative design contract and contains the complete token-swap table for every element.

The biggest implementation decision already resolved by the UI-SPEC is how to apply VS Code hex tokens in Tailwind v4: arbitrary value syntax (`bg-[#1e1e1e]`, `border-l-[#4ec994]`) applied inline on JSX elements. Tailwind v4 fully supports this and requires no `tailwind.config.js` — the `@tailwindcss/vite` plugin processes arbitrary values at build time. An alternative of CSS custom properties declared in `index.css` as `--vsc-*` variables is also viable and may reduce repetition, but either approach is correct.

The breadcrumb requires careful data derivation: `group.displayName` comes from looking up `groups` by `activeSegment.groupId` — both `groups` and `activeSegment` are already exposed by `useApp()`, so no context changes are needed. The stats bar requires extending the existing `stats` useMemo to compute `phasesDone`, `phasesTotal`, and `activePhaseName` from the existing `activeProject.milestones[].phases[]` array.

**Primary recommendation:** Execute as three sequential tasks aligned to the three files in scope: (1) index.css font change, (2) DashboardPage stats + breadcrumb + phase rows, (3) ShellLayout token swaps. Each task is independently verifiable by visual inspection.

---

## Standard Stack

### Core (already installed — no new dependencies)

| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| React | 19.0 | Component rendering | Named exports, function components, `useMemo` |
| Tailwind CSS | 4.0 | Utility styling | `@tailwindcss/vite` plugin; no `tailwind.config.js`; arbitrary values via `[]` syntax |
| TypeScript | 5.9 | Type safety | Strict mode; `noUnusedLocals`, `noUnusedParameters` enforced |
| Vite | 6.0 | Build + dev server | `tsc -b && vite build` for production |

**No new packages required.** This phase involves zero npm installs.

### Tailwind v4 Arbitrary Value Pattern (HIGH confidence)

Tailwind v4 supports arbitrary CSS values inline using bracket notation. This works without any config file:

```tsx
// Background color from hex
className="bg-[#1e1e1e]"

// Border color from hex
className="border-[#474747]"

// Left border only — width + color
className="border-l-[3px] border-l-[#4ec994]"

// Text color from hex
className="text-[#cccccc]"

// Hover state with arbitrary value
className="hover:bg-[#2a2d2e]"
```

Tailwind v4 processes these at build time via the Vite plugin. No purge configuration needed — the plugin scans TSX/JS files automatically.

**Alternative — CSS custom properties:** Declaring tokens in `index.css` and referencing them:

```css
/* index.css */
:root {
  --vsc-editor-bg: #1e1e1e;
  --vsc-sidebar-bg: #252526;
}
```

```tsx
className="bg-[var(--vsc-editor-bg)]"
```

This reduces repetition but adds indirection. Either approach is valid. The UI-SPEC uses the direct hex approach.

---

## Architecture Patterns

### Files in Scope (exhaustive)

```
frontend/src/
├── index.css              -- Add body font-family (1-line change)
├── pages/DashboardPage.tsx -- Stats bar + breadcrumb + phase row classes
└── ShellLayout.tsx        -- Sidebar color token swaps
```

**Files explicitly NOT touched:** `Drawer.tsx`, `context.tsx`, `api.ts`, any backend file.

### Pattern 1: Stats useMemo Extension

The existing `stats` useMemo in DashboardPage computes `completion`, `activePhases`, `milestones`, `driftLabel`. Extend it to add `phasesDone`, `phasesTotal`, and `activePhaseName`:

```tsx
// Source: DashboardPage.tsx existing pattern, extended per UI-SPEC
const stats = useMemo(() => {
  if (!activeProject) return null;
  const phases = activeProject.milestones.flatMap((m) => m.phases);
  const total = phases.length;
  const complete = phases.filter((p) => p.status === "complete").length;
  const completion = total ? Math.round((complete / total) * 100) : 0;
  // NEW: replace milestones/activePhases with phasesDone/phasesTotal/activePhaseName
  const phasesDone = complete;
  const phasesTotal = total;
  const activePhaseName =
    phases.find((p) => p.status === "in_progress")?.title ?? "—";
  let driftLabel = "No drift";
  const hasM = phases.some((p) => p.drift === "major");
  const hasN = phases.some((p) => p.drift === "minor");
  if (hasM) driftLabel = "Major drift";
  else if (hasN) driftLabel = "Minor drift";
  return { completion, phasesDone, phasesTotal, activePhaseName, driftLabel, gsdVersion: activeProject.version };
}, [activeProject]);
```

### Pattern 2: Breadcrumb Derivation

All three breadcrumb segments are derivable from existing `useApp()` context — no context changes needed:

```tsx
// Source: context.tsx — useApp() exposes groups, activeSegment, activeProject
const { activeProject, activeSegment, groups } = useApp();

const activeGroup = groups.find((g) => g.id === activeSegment?.groupId) ?? null;
const groupName = activeGroup?.displayName ?? "—";
const projectName = activeProject?.name ?? "—";

const phases = activeProject?.milestones.flatMap((m) => m.phases) ?? [];
const activePhaseTitle =
  phases.find((p) => p.status === "in_progress")?.title ??
  phases.filter((p) => p.status === "complete").sort(byLastUpdated)[0]?.title ??
  "—";
```

Note: `activeSegment` is already returned by `useApp()` (confirmed in `context.tsx` line 25: `activeSegment: SegmentPayload | null`). DashboardPage currently only destructures `{ activeProject, loading }` — it must also destructure `activeSegment` and `groups`.

### Pattern 3: Left Border Status Mapping

Phase row left border color is determined by `p.status`. Use a helper function or inline ternary:

```tsx
function statusBorderClass(status: string): string {
  switch (status) {
    case "complete":
      return "border-l-[#4ec994]";
    case "in_progress":
    case "needs_verification":
      return "border-l-[#007acc]";
    default:
      return "border-l-[#474747]";
  }
}
```

Applied on the phase row button:

```tsx
className={`w-full rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-left transition-colors
  hover:bg-[#2a2d2e] border-l-[3px] ${statusBorderClass(p.status)}`}
```

### Pattern 4: Token Swap in ShellLayout

ShellLayout changes are class-level replacements only. The UI-SPEC contains the full mapping table. No structural JSX changes — only `className` string replacements.

Key swaps (summary):
- `bg-zinc-950` → `bg-[#1e1e1e]` (outer wrapper)
- `bg-zinc-900/80` → `bg-[#252526]` (aside)
- `border-zinc-800` → `border-[#474747]` (all borders)
- `bg-zinc-800` / `hover:bg-zinc-800/60` → `bg-[#2a2d2e]` / `hover:bg-[#2a2d2e]` (nav active/hover)
- `text-zinc-100` / `text-zinc-400` / `text-zinc-500` → `text-[#cccccc]` / `text-[#858585]`

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Breadcrumb data derivation | Custom state/context | Existing `useApp()` `groups` + `activeSegment` | Both already in context; zero new code in `context.tsx` |
| Color token system | Design token library | Tailwind v4 arbitrary values or CSS custom properties | Tailwind v4 + Vite plugin handles it natively |
| Status-to-color mapping | Lookup table in separate file | Inline helper function in DashboardPage.tsx | Scope is local; a file-level function is sufficient |

**Key insight:** This phase is a reskin, not a feature build. Every helper function and data source already exists — the work is targeted replacement of class strings and extension of one useMemo.

---

## Common Pitfalls

### Pitfall 1: Border-l overriding the full border declaration

**What goes wrong:** Using `border border-[#474747] border-l-[3px] border-l-[#4ec994]` — if Tailwind's generated CSS orders the full `border` shorthand after `border-l`, it overrides the left border color.

**Why it happens:** CSS specificity — `border` is shorthand and resets all sides including left.

**How to avoid:** In Tailwind v4, utility classes are applied in source order. Set the left border after the full border shorthand in the class string. Alternatively, use `border-r border-t border-b border-[#474747]` (only the non-left sides) and `border-l-[3px] border-l-[#4ec994]` explicitly, avoiding the `border` shorthand entirely.

**Warning signs:** Left border renders the same color as the other three sides regardless of status.

### Pitfall 2: TypeScript `noUnusedLocals` breaks after removing `milestones`/`activePhases` from stats

**What goes wrong:** Removing `milestones` and `activePhases` from the stats useMemo while the old card JSX still references them causes a TS compile error. Removing the old card JSX references while stats still computes the old values causes `noUnusedLocals` errors.

**Why it happens:** `tsconfig.json` has `"noUnusedLocals": true` and `"noUnusedParameters": true` — both are enforced by `tsc -b` in the build.

**How to avoid:** Update stats useMemo and the JSX cards in the same edit. Do not leave half-removed state.

**Warning signs:** `tsc -b` fails with "Property 'milestones' does not exist" or "'milestones' is declared but its value is never read."

### Pitfall 3: Missing `activeSegment` and `groups` destructure in DashboardPage

**What goes wrong:** Breadcrumb requires `activeSegment.groupId` to look up group name. DashboardPage currently only destructures `{ activeProject, loading }` from `useApp()`.

**Why it happens:** Breadcrumb is new in this phase — the existing destructure is minimal.

**How to avoid:** Add `activeSegment` and `groups` to the `useApp()` destructure at the top of `DashboardPage`. Both are already in the `Ctx` type and `useApp()` return value — no context changes needed.

**Warning signs:** `activeGroup` is always `null`; breadcrumb always shows `—` for the group name.

### Pitfall 4: Tailwind v4 does not support `tailwind.config.js` theme extension

**What goes wrong:** Attempting to add VS Code color tokens via a `tailwind.config.js` `theme.extend.colors` block — this is the Tailwind v3 pattern and does not work in v4.

**Why it happens:** Tailwind v4 uses CSS-first configuration via `@theme` blocks in CSS, not a JS config file.

**How to avoid:** Use arbitrary values (`bg-[#1e1e1e]`) or declare CSS custom properties in `index.css` and reference via `bg-[var(--vsc-editor-bg)]`. Do not create or edit a `tailwind.config.js`.

**Warning signs:** Custom color name classes like `bg-vsc-editor` don't generate any CSS output.

### Pitfall 5: `bg-zinc-900/40` opacity modifier syntax doesn't have an arbitrary-value equivalent without a variable

**What goes wrong:** The current phase row has `bg-zinc-900/40` (zinc-900 at 40% opacity). The replacement is `bg-[#1e1e1e]` (solid color) — this is intentional per UI-SPEC. But if someone tries to add opacity to the arbitrary hex via `bg-[#1e1e1e]/40`, this is valid Tailwind v4 syntax and will work — but the UI-SPEC does not call for it.

**How to avoid:** Use solid `bg-[#1e1e1e]` on cards and phase rows per the UI-SPEC. Do not add opacity modifiers.

---

## Code Examples

### Stats Bar Card (updated)

```tsx
{/* Card 1 — unchanged content, updated classes */}
<div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
  <div className="text-2xl font-semibold text-[#cccccc]">{stats?.completion ?? 0}%</div>
  <div className="text-xs text-[#858585]">Completion</div>
</div>

{/* Card 2 — new content: phases done/total */}
<div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
  <div className="text-2xl font-semibold text-[#cccccc]">
    {stats?.phasesDone ?? 0} / {stats?.phasesTotal ?? 0}
  </div>
  <div className="text-xs text-[#858585]">Phases done</div>
</div>

{/* Card 3 — new content: active phase name (text-sm, not text-2xl) */}
<div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
  <div className="text-sm font-semibold text-[#cccccc] truncate">
    {stats?.activePhaseName ?? "—"}
  </div>
  <div className="text-xs text-[#858585]">Active phase</div>
</div>

{/* Card 4 — unchanged content, updated classes */}
<div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
  <div className="text-sm font-semibold text-[#cccccc]">{stats?.driftLabel}</div>
  <div className="text-xs text-[#858585]">Drift</div>
</div>
```

### Breadcrumb Component (inline in DashboardPage)

```tsx
{/* Breadcrumb — above stats grid */}
<div className="mb-4 flex items-center gap-1 py-2 text-sm font-semibold">
  <span className="text-[#858585]">{groupName}</span>
  <span className="mx-1 text-[#474747]">/</span>
  <span className="text-[#858585]">{projectName}</span>
  <span className="mx-1 text-[#474747]">/</span>
  <span className="max-w-[240px] truncate text-[#cccccc]">{activePhaseTitle}</span>
</div>
```

### Phase Row Button (updated)

```tsx
<button
  type="button"
  key={`${p.number}-${p.title}`}
  className={`w-full rounded-md border border-[#474747] border-l-[3px] ${statusBorderClass(p.status)} bg-[#1e1e1e] p-4 text-left transition-colors hover:bg-[#2a2d2e]`}
  onClick={() => { setSelected(p); setDrawerOpen(true); }}
>
  <div className="flex items-center justify-between gap-2">
    <span className="font-mono font-medium text-[#cccccc]">
      {String(p.number).padStart(2, "0")} — {p.title}
    </span>
    <div className="flex items-center gap-2">
      <span className="text-xs text-[#858585]">{statusLabel(p.status)}</span>
      <span className="text-xs text-[#858585]">{fmtDate(p.last_updated)}</span>
    </div>
  </div>
  {p.goal && <p className="mt-1 line-clamp-2 text-xs text-[#858585]">{p.goal}</p>}
</button>
```

### index.css Font Addition

```css
@import "tailwindcss";

body {
  font-family: "Segoe UI", system-ui, sans-serif;
}
```

---

## State of the Art

| Old Approach | Current Approach | Relevance |
|--------------|------------------|-----------|
| Tailwind v3 `tailwind.config.js` theme extension | Tailwind v4 arbitrary values `bg-[#hex]` or `@theme` in CSS | Use arbitrary values — no config file |
| Tailwind v3 `@apply` in component CSS files | Tailwind v4 inline utility classes | Project already uses inline — continue this pattern |
| Zinc color scale (`bg-zinc-950`, `text-zinc-100`) | VS Code Dark+ hex tokens via arbitrary values | This phase performs the migration |

---

## Open Questions

1. **Border shorthand order in Tailwind v4**
   - What we know: Tailwind v4 generates CSS in utility declaration order. Setting `border border-[#474747]` first, then `border-l-[3px] border-l-[#color]` should override the left side.
   - What's unclear: Whether Tailwind v4's CSS output ordering guarantees left-border utility wins over the shorthand.
   - Recommendation: During implementation, verify visually that the left border color differs from the other three sides. If not, switch to `border-r border-t border-b border-[#474747]` + `border-l-[3px] border-l-[#color]` to avoid the shorthand.

2. **Active phase name card overflow**
   - What we know: Phase titles can be long strings (e.g., "Worktree Deduplication and Badge Display"). The card is `text-center` with fixed grid width.
   - What's unclear: Whether `truncate` alone on the value div is sufficient given the card is `text-center`.
   - Recommendation: Use `truncate` on the value element and test with a long title. If centering conflicts with truncate, use `text-left` only on that card's value or limit with `max-w-full`.

---

## Environment Availability

Step 2.6: SKIPPED — this phase is purely frontend code changes. No new external tools, services, CLIs, or runtimes are required. Node.js/npm (for Vite dev server and build) are already in use by the project.

---

## Project Constraints (from CLAUDE.md)

Directives the planner must verify compliance with:

| Constraint | Impact on This Phase |
|------------|----------------------|
| Tech stack frozen: React 19 / Tailwind CSS v4 / Vite 6 / TypeScript 5.9 | No new libraries; no stack changes — compliant |
| Windows only (Edge WebView2) | Segoe UI font is always available on Windows — safe to use |
| App is read-only — never writes to project files | This phase touches only `frontend/src/` — no backend changes — compliant |
| Settings format: `%LOCALAPPDATA%\WinGSDMonitor\settings.json` PascalCase | Not touched by this phase |
| `PascalCase.tsx` for React component files | No new files added; existing naming unchanged |
| Named exports only (no default exports for pages/components) | `DashboardPage` already a named export; no new components |
| Tailwind utility classes inline — no CSS modules | Phase follows this; arbitrary values inline on JSX |
| Dark theme via zinc scale → migrating to VS Code hex tokens | This phase performs the migration |
| `tsconfig.json` strict mode: `noUnusedLocals`, `noUnusedParameters` | Removing `milestones`/`activePhases` from stats must happen in sync with JSX card updates |
| `type` keyword for pure type imports | No new type imports expected; follow pattern if any added |

---

## Sources

### Primary (HIGH confidence)

- Codebase: `frontend/src/pages/DashboardPage.tsx` — current stats useMemo, phase list, drawer integration
- Codebase: `frontend/src/ShellLayout.tsx` — complete class inventory for token-swap reference
- Codebase: `frontend/src/context.tsx` — confirmed `activeSegment` and `groups` are in `useApp()` return value
- Codebase: `frontend/src/api.ts` — confirmed `PhasePayload.status` field values, `SegmentPayload.groupId`
- Codebase: `frontend/package.json` — confirmed Tailwind 4.0, React 19, Vite 6 installed
- Codebase: `frontend/vite.config.ts` — confirmed `@tailwindcss/vite` plugin in use (no `tailwind.config.js`)
- Codebase: `frontend/src/index.css` — confirmed single-line `@import "tailwindcss"` (space for body addition)
- Design contract: `.planning/phases/02-visual-redesign/02-UI-SPEC.md` — authoritative token-swap table, component anatomy, interaction spec
- User decisions: `.planning/phases/02-visual-redesign/02-CONTEXT.md` — 15 locked decisions (D-01 through D-15)

### Secondary (MEDIUM confidence)

- Tailwind CSS v4 arbitrary value behavior — verified by presence of `@tailwindcss/vite` plugin and Tailwind v4 docs pattern (inline `bg-[#hex]` is the documented v4 approach; no `tailwind.config.js` is created in this project confirming v4 CSS-first configuration)

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — all packages confirmed installed in package.json; no new installs
- Architecture patterns: HIGH — current code fully read; all extension points identified from source
- Pitfalls: HIGH — derived from actual code inspection (noUnusedLocals in tsconfig, existing destructure pattern in DashboardPage, Tailwind v4 no-config-file confirmation)
- UI-SPEC completeness: HIGH — all 15 locked decisions have corresponding implementation detail in 02-UI-SPEC.md

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable codebase; no fast-moving external dependencies)
