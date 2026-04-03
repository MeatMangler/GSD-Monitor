---
status: draft
phase: 02
phase_name: visual-redesign
created: 2026-04-03
tool: none
registry: not-applicable
---

# UI-SPEC: Phase 02 — Visual Redesign

## Purpose

Define the visual and interaction contract for replacing the current zinc-scale dark theme with the VS Code Dark+ palette, adding a stats bar with correct content, adding a breadcrumb, and adding colored left-border phase status indicators.

Files in scope: `frontend/src/pages/DashboardPage.tsx`, `frontend/src/ShellLayout.tsx`, `frontend/src/index.css`. No new pages. No backend changes. No new component library.

---

## Design System

**Tool:** none — no shadcn, no component library. Tailwind CSS v4 utility classes inline, arbitrary value syntax for VS Code hex tokens (e.g., `bg-[#1e1e1e]`).

**Styling approach:** Tailwind utility classes inline. No CSS modules, no styled components. Custom property approach is an acceptable alternative to arbitrary values if the executor prefers — declare tokens in `index.css` as `--vsc-*` variables and reference them via Tailwind arbitrary values.

**Registry:** not applicable.

---

## Color Contract

Source: CONTEXT.md D-13 (locked).

### Token Table

| Token name | Hex | Role | Coverage |
|---|---|---|---|
| `vsc-editor-bg` | `#1e1e1e` | Main content area background | ~60% dominant surface |
| `vsc-sidebar-bg` | `#252526` | Sidebar/aside background | ~30% secondary surface |
| `vsc-hover` | `#2a2d2e` | List item hover state | Interactive surface |
| `vsc-border` | `#474747` | All borders (cards, rows, sidebar divider) | Structural separator |
| `vsc-accent` | `#007acc` | Active phase border, active nav item, GSD-version badge, `in_progress` phase left border | Reserved for: active/selected state only |
| `vsc-green` | `#4ec994` | `complete` phase left border | Reserved for: complete status only |
| `vsc-text-primary` | `#cccccc` | Primary body text, stat values, phase titles | High-contrast readable content |
| `vsc-text-muted` | `#858585` | Labels, secondary text, status labels, dates, card sublabels | De-emphasized supporting text |
| `vsc-gray-border` | `#474747` | `not_started` phase left border | Reserved for: not-started status only |

### 60/30/10 Application

- **60% — editor bg `#1e1e1e`:** `<main>` content area, stats card fill, phase row fill, drawer background.
- **30% — sidebar bg `#252526`:** `<aside>` sidebar, worktree tooltip background.
- **10% — accent `#007acc`:** Exclusively on `in_progress` phase left border, active NavLink highlight, GSD-version badge. Do not use accent for decoration.

### Semantic color: destructive

No destructive actions in this phase. `text-red-400` is already used for error display in ShellLayout — leave unchanged.

---

## Typography Contract

Source: CONTEXT.md D-14, D-15 (locked).

### Font Stack

```css
font-family: "Segoe UI", system-ui, sans-serif;
```

Apply at `body` level in `frontend/src/index.css`. Windows-only app; Segoe UI is always present.

### Monospace (phase numbers, code)

```css
font-family: "Cascadia Code", "Consolas", monospace;
```

Applied inline where phase numbers are rendered (e.g., `font-mono` Tailwind class).

### Size Scale (exactly 4 sizes)

| Role | Size | Weight | Line-height | Usage |
|---|---|---|---|---|
| stat-value | 24px (text-2xl) | 600 (semibold) | 1.2 | Stat card primary number (%, counts) |
| body | 14px (text-sm) | 400 (normal) | 1.5 | Phase title, goal text, nav items, labels |
| label | 12px (text-xs) | 400 (normal) | 1.4 | Stat sublabels, status text, dates, drawer section headers |
| heading | 13px (text-sm) | 600 (semibold) | 1.2 | "GSD Monitor" app title, breadcrumb segments |

**Weights declared: 2** — regular (400) and semibold (600) only. No bold (700), no medium (500).

---

## Spacing Contract

8-point scale. All spacing values are multiples of 4px.

| Token | Value | Usage |
|---|---|---|
| 4px (p-1) | 4px | Inline badge padding, tight gaps |
| 8px (p-2 / gap-2) | 8px | Nav item horizontal padding, worktree row padding |
| 12px (p-3) | 12px | Sidebar header padding, sidebar section padding |
| 16px (p-4) | 16px | Phase row padding, stat card padding |
| 24px (p-6) | 24px | Dashboard content area outer padding |
| 32px (mb-8) | 32px | Major section separation |

**Touch targets:** No interactive touch targets below 32px height. Phase row buttons must be at minimum 48px tall (padding achieves this via p-4 on both axes).

**Exception — breadcrumb:** 8px vertical padding, 0 horizontal padding (sits flush at content top before stats bar).

---

## Spacing: Colored Left Border

Source: CONTEXT.md D-06 (locked), discretion on exact width.

**Border width: 3px** (between 2–4px; 3px matches VS Code's own active item indicator).

Applied as `border-l-[3px]` on each phase row button. Color is determined by `status`:

| Status value | Left border color | Tailwind arbitrary class |
|---|---|---|
| `complete` | `#4ec994` | `border-l-[#4ec994]` |
| `in_progress` | `#007acc` | `border-l-[#007acc]` |
| `needs_verification` | `#007acc` | `border-l-[#007acc]` (same as in_progress) |
| `not_started` (default) | `#474747` | `border-l-[#474747]` |

The right/top/bottom border uses `vsc-border` `#474747` via `border-[#474747]` (replace existing `border-zinc-800`).

---

## Component Inventory

No new components. All changes are class-level swaps and JSX additions within existing files.

### Stats Bar (DashboardPage.tsx)

Replace the 4-card grid content (CONTEXT.md D-01 through D-05, locked):

| Card position | Current content | New content |
|---|---|---|
| 1 | `completion %` | `completion %` — unchanged |
| 2 | `milestones` count | `phases done / phases total` (e.g., "3 / 7") |
| 3 | `active phases` count | `active phase name` — title of first `in_progress` phase, or `—` |
| 4 | `drift label` | `drift label` — unchanged |

Layout: keep `grid grid-cols-2 gap-3 md:grid-cols-4`.

Card anatomy:
- Container: `rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center`
- Primary value: `text-2xl font-semibold text-[#cccccc]` (was `text-white`)
- Sublabel: `text-xs text-[#858585]` (was `text-zinc-500`)

Active phase name card: value is `text-sm` (not `text-2xl`) since it is a string, not a number. Keep `font-semibold text-[#cccccc]`.

### Breadcrumb (DashboardPage.tsx)

Source: CONTEXT.md D-09, D-10, D-11, D-12 (locked).

Position: top of DashboardPage content area, above the stats cards. Not in ShellLayout.

Markup pattern:

```
[group.displayName] / [activeProject.name] / [active phase title or last complete phase title or —]
```

Separator: ` / ` rendered as `<span className="text-[#474747] mx-1">/</span>`.

Segment style: `text-sm font-semibold text-[#858585]` for non-terminal segments; `text-sm font-semibold text-[#cccccc]` for the terminal segment (active phase).

Truncation: terminal segment truncates with `truncate max-w-[240px]` when long. Earlier segments are short (repo/project names) — no truncation needed.

Data derivation:
- `group.displayName`: look up `groups` from `useApp()` by `activeSegment.groupId` (may require exposing `activeSegment` or deriving inline from `groups` + `selectedGroupId`).
- `activeProject.name`: already available from `useApp().activeProject`.
- Active phase title: `phases.find(p => p.status === 'in_progress')?.title ?? phases.filter(p => p.status === 'complete').sort(byLastUpdated)[0]?.title ?? '—'`.

### Phase List Rows (DashboardPage.tsx)

Source: CONTEXT.md D-06, D-07, D-08 (locked).

Current classes on row button:
```
rounded-lg border border-zinc-800 bg-zinc-900/40 p-4 text-left transition hover:border-zinc-600
```

Replacement classes:
```
rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-left transition
  hover:bg-[#2a2d2e]
  border-l-[3px] {status-border-color}
```

Remove `hover:border-zinc-600` — hover state is expressed by background change, not border color change.

Phase title: `font-medium text-[#cccccc]` (was `text-zinc-100`).

Status label + date: `text-xs text-[#858585]` (was `text-zinc-500`).

Goal text: `mt-1 line-clamp-2 text-xs text-[#858585]` (was `text-zinc-500`).

Sort: unchanged — `byLastUpdated` comparator, recency descending (CONTEXT.md D-07, locked).

Drawer: unchanged (CONTEXT.md D-08, locked).

### ShellLayout.tsx — Sidebar

Color token swaps only:

| Current class | Replacement | Applied to |
|---|---|---|
| `bg-zinc-950` | `bg-[#1e1e1e]` | Outer shell wrapper `div` |
| `bg-zinc-900/80` | `bg-[#252526]` | `<aside>` |
| `border-zinc-800` | `border-[#474747]` | Sidebar right border, header bottom border |
| `bg-zinc-950` | `bg-[#252526]` | `<select>` elements |
| `border-zinc-700` | `border-[#474747]` | `<select>` border |
| `text-zinc-400` | `text-[#858585]` | Labels, nav inactive |
| `text-zinc-100` | `text-[#cccccc]` | App title, selected option |
| `text-zinc-500` | `text-[#858585]` | Subtitle, inactive nav |
| `bg-zinc-800` | `bg-[#2a2d2e]` | Active NavLink bg |
| `hover:bg-zinc-800/60` | `hover:bg-[#2a2d2e]` | Nav item hover |
| `hover:text-zinc-200` | `hover:text-[#cccccc]` | Nav item hover text |

Worktree badge:
- Badge: `bg-[#2a2d2e] px-1.5 py-0.5 text-xs text-[#858585]` (was `bg-zinc-700 text-zinc-300`)
- Tooltip container: `bg-[#252526] border-[#474747]` (was `bg-zinc-900 border-zinc-700`)
- Branch text in tooltip: `text-[#cccccc]` (was `text-zinc-300`)
- Path segment: `text-[#858585]` (was `text-zinc-500`)
- "main" indicator: `text-[#858585]` (was `text-zinc-600`)

### index.css

Add font-family declaration:

```css
@import "tailwindcss";

body {
  font-family: "Segoe UI", system-ui, sans-serif;
}
```

No other changes to index.css.

---

## Copywriting Contract

### Stats Bar Labels

| Card | Value display | Sublabel |
|---|---|---|
| Completion | `{N}%` | `Completion` |
| Phases | `{done} / {total}` | `Phases done` |
| Active phase | `{phase title}` or `—` | `Active phase` |
| Drift | `{No drift / Minor drift / Major drift}` | `Drift` |

### Breadcrumb

- Format: `{repo name} / {project name} / {active phase title}`
- No label prefix (no "You are here:" or similar)
- Terminal `—` when no active or complete phase exists

### Empty States

| Condition | Location | Copy |
|---|---|---|
| No project selected | DashboardPage | `Add scan roots in Settings and select a project.` (unchanged — already correct) |
| Loading | DashboardPage | `Loading…` (unchanged) |
| No active phase for breadcrumb | Breadcrumb terminal segment | `—` (em dash, no additional copy) |

### Error States

| Condition | Location | Copy |
|---|---|---|
| API error loading groups | ShellLayout | `{error message text from API}` in `text-red-400` (unchanged) |

### Destructive Actions

None in this phase. No confirmation dialogs needed.

---

## Interaction Contract

### Phase Row: Hover

- Background changes from `#1e1e1e` to `#2a2d2e` via `hover:bg-[#2a2d2e]`.
- Left border color does not change on hover — status color is invariant.
- No scale or shadow transitions.
- Transition: `transition-colors` (Tailwind default transition on color properties only).

### Phase Row: Click

Opens the existing Drawer with plan/research/validation content. No change to click behavior or Drawer internals.

### Nav Item: Active

Active NavLink renders `bg-[#2a2d2e] text-[#cccccc]`. No left border on nav items (left border is phase-list-only).

### Selects

Selects (`<select>`) retain default browser focus ring — no custom focus styling added in this phase.

### Worktree Tooltip

CSS-only via `group/group-hover:visible` — no JS state. Behavior unchanged from Phase 01 implementation.

---

## States Required

| Component | States |
|---|---|
| Stats bar | loading (no activeProject), loaded with data |
| Phase row | default, hover, (active/clicked is handled by Drawer open state) |
| Phase row left border | complete, in_progress / needs_verification, not_started |
| Breadcrumb | has active phase, has only complete phases, has no phases (`—`) |
| Nav item | active, inactive, inactive-hover |

---

## Accessibility

- Color is never the sole indicator: phase rows also show `statusLabel()` text alongside the left border color.
- `<button type="button">` already present on phase rows — no change.
- Breadcrumb does not use `<nav aria-label="breadcrumb">` in this phase — it is a visual-only element. Acceptable for a desktop-only local tool.
- Contrast: `#cccccc` on `#1e1e1e` = 10.7:1 (passes WCAG AA). `#858585` on `#1e1e1e` = 4.5:1 (passes WCAG AA minimum).

---

## Files to Touch

| File | Change type |
|---|---|
| `frontend/src/index.css` | Add `body { font-family: "Segoe UI", system-ui, sans-serif; }` |
| `frontend/src/pages/DashboardPage.tsx` | Stats bar content + classes, breadcrumb addition, phase row classes |
| `frontend/src/ShellLayout.tsx` | Color token swaps across all elements |

**Files NOT touched:** `Drawer.tsx`, `context.tsx`, `api.ts`, all backend files.

---

## Pre-Population Sources

| Source | Decisions used |
|---|---|
| CONTEXT.md D-01 to D-15 | All 15 locked decisions: stats bar content, phase list indicator style, breadcrumb position and segments, VS Code hex tokens, font family |
| REQUIREMENTS.md DASH-01 to DASH-04 | Success criteria drove state requirements and component inventory |
| DashboardPage.tsx (scanned) | Existing class names for token-swap table, existing `statusLabel()` helper confirmed reusable |
| ShellLayout.tsx (scanned) | Full class inventory for sidebar token-swap table |
| api.ts (scanned) | `PhasePayload`, `GroupPayload`, `SegmentPayload` interfaces confirm data available at render time |
| CONTEXT.md Claude's Discretion | Border width (3px), breadcrumb truncation (truncate max-w-[240px] on terminal segment), status label format (keep existing `statusLabel()`) |

---

*Phase: 02-visual-redesign*
*UI-SPEC drafted: 2026-04-03*
