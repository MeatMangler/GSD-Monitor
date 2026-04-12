---
phase: 9
phase_name: Drift Computation
status: approved
created: 2026-04-12
reviewed_at: 2026-04-12
design_system: none (Tailwind CSS v4, no shadcn)
---

# UI-SPEC: Phase 9 — Drift Computation

## Phase Boundary Note

Phase 9 is a **pure backend change**. It produces no new pages, no new UI components, and no schema changes visible to the user. The `DriftIndicator` enum field (`drift`) already exists on `PhasePayload` and is already consumed by `DashboardPage.tsx`. This phase replaces the hardcoded `DEFERRED` value with real computed values.

**This UI-SPEC documents:**
1. The existing design tokens and patterns the executor must not break
2. The downstream visual contract that Phase 9's `DriftIndicator` output enables (consumed by Phase 10)
3. The badge color contract that `DriftPage` (Phase 10) will use — defined here so it can be validated against the API output Phase 9 produces

---

## Design System

**Tool:** Tailwind CSS v4 (no `tailwind.config.js` — utility classes only via `@tailwindcss/vite` plugin)
**Component library:** None (shadcn not initialized — not applicable for Windows-only desktop app)
**Icon library:** None
**Typography plugin:** `@tailwindcss/typography` (used for markdown prose rendering)
**Font:** `"Segoe UI", system-ui, sans-serif` (declared in `frontend/src/index.css`)

Source: `frontend/package.json`, `frontend/src/index.css`

---

## Existing Design Tokens (Pre-Populated from Codebase)

All tokens are raw Tailwind CSS v4 hex values extracted from `ShellLayout.tsx` and `DashboardPage.tsx`. Phase 9 must not introduce any new UI surfaces, but these tokens define the contract Phase 10 inherits.

### Color Scale

| Role | Hex | Tailwind Utility | Where Used |
|------|-----|-----------------|------------|
| App background | `#1e1e1e` | `bg-[#1e1e1e]` | `ShellLayout` main area, stat cards |
| Sidebar / secondary surface | `#252526` | `bg-[#252526]` | Sidebar, select inputs |
| Hover / elevated surface | `#2a2d2e` | `bg-[#2a2d2e]` | Nav active state, card hover, worktree tooltip |
| Border | `#474747` | `border-[#474747]` | All card borders, sidebar border, input borders |
| Primary text | `#cccccc` | `text-[#cccccc]` | Phase titles, stat values, nav active |
| Muted text / labels | `#858585` | `text-[#858585]` | Secondary text, labels, dates, empty states |
| Blue accent | `#007acc` | `text-[#007acc]` / `bg-[#007acc]/30` | In-progress phase left border, GSD version badge |
| Green accent | `#4ec994` | `border-l-[#4ec994]` | Complete phase left border |
| Error text | `red-400` | `text-red-400` | Error state in ShellLayout loading block |

Source: `frontend/src/ShellLayout.tsx`, `frontend/src/pages/DashboardPage.tsx`

### 60/30/10 Color Split

- **60% dominant surface:** `#1e1e1e` — main content area, all page backgrounds
- **30% secondary surface:** `#252526` — sidebar, inputs, elevated cards
- **10% accent:** `#007acc` (blue) for active/in-progress state; `#4ec994` (green) for completion; drift badge colors listed below

---

## Spacing Scale

8-point grid. Values extracted from existing codebase patterns:

| Value | Tailwind Class | Usage |
|-------|---------------|-------|
| 4px | `p-1`, `gap-1` | Tight inline spacing (breadcrumb separators) |
| 8px | `p-2`, `gap-2` | Nav padding, gap between badge elements |
| 12px | `p-3` | Sidebar section padding |
| 16px | `p-4` | Stat card padding, phase card padding |
| 24px | `p-6` | Page content padding (`DashboardPage`) |
| 32px | `p-8` | Stub page padding (used by current `DriftPage`, `QuickTasksPage`, `VerificationPage`) |

**Legacy exceptions:** `p-1.5`/`px-1.5` (6px) exists in pre-Phase-9 badge components — do not introduce in new Phase 10 components.

Source: `frontend/src/ShellLayout.tsx`, `frontend/src/pages/DashboardPage.tsx`

---

## Typography

Exactly 3 sizes in use across the application:

| Size | Tailwind Class | Weight | Line Height | Usage |
|------|---------------|--------|-------------|-------|
| 24px | `text-2xl` | `font-semibold` (600) | default | Stat card numeric values |
| 14px (default) | `text-sm` | `font-medium` (500) or `font-semibold` (600) | `leading-5` (20px / 1.25rem) | Phase titles, nav items, select inputs, body text |
| 12px | `text-xs` | `font-medium` (500) or normal (400) | default | Labels, dates, stat card captions, badges, section headers |

**Two weights only:** 400 (normal, used for dates and secondary labels) and 600/500 (`font-semibold`/`font-medium`, used for titles and values).

Markdown prose: `prose prose-invert prose-sm max-w-none` via `@tailwindcss/typography`.

Source: `frontend/src/pages/DashboardPage.tsx`

---

## Drift Badge Color Contract

Phase 9 produces `DriftIndicator` values. Phase 10 renders them as color-coded badges. This contract is defined here so the backend output (Phase 9) and frontend rendering (Phase 10) are aligned from the start.

**Required by DRFT-04:**

| DriftIndicator | Badge Color | Hex | Tailwind Pattern |
|---------------|-------------|-----|-----------------|
| `major` | Red | `#f87171` (red-400) | `bg-red-400/20 text-red-400` |
| `minor` | Yellow | `#fbbf24` (amber-400) | `bg-amber-400/20 text-amber-400` |
| `none` | Muted green | `#4ec994` | `bg-[#4ec994]/20 text-[#4ec994]` |
| `deferred` | Gray | `#858585` | `bg-[#474747] text-[#858585]` |

Badge shape: `rounded px-1.5 py-0.5 text-xs font-medium` — consistent with existing GSD version badge pattern in `DashboardPage.tsx`.

Source: REQUIREMENTS.md DRFT-04, extrapolated from existing `bg-[#007acc]/30` badge pattern in DashboardPage.

---

## Copywriting Contract

Phase 9 introduces no new user-facing copy. The following copy is inherited from existing stubs and will be replaced in Phase 10.

**Current stub copy (will be replaced in Phase 10, not Phase 9):**
- `DriftPage`: "Drift detection coming in v2." (`text-[#858585]`)
- `QuickTasksPage`: "Quick tasks coming in v2." (`text-[#858585]`)
- `VerificationPage`: "Verification detail coming in v2." (`text-[#858585]`)

**Empty state copy contract (for Phase 10 — defined here for planner continuity):**
- DriftPage no phases: "No phases found for this project."
- DriftPage all DEFERRED/hidden: "All phases are un-started. Show N un-started →"
- QuickTasksPage empty: "No quick tasks found for this project." (per QTSK-04 — not an error)

**Error state copy contract:**
- API failure: "Failed to load [page name]. Check that the backend is running."
- Pattern: problem description + implicit "retry by navigating away and back"

**Destructive actions in Phase 9:** None. App is read-only.

---

## Interaction Contract

Phase 9 has no interactive surfaces. The following interaction contracts are pre-defined for Phase 10 consumers:

### Drift Table (Phase 10, DRFT-02 through DRFT-05)
- Sorted by severity: MAJOR rows first, then MINOR, then NONE, then DEFERRED
- Un-started phases (no plan + NOT_STARTED) hidden by default behind "Show N un-started" toggle
- Toggle is a plain `<button>` with `text-[#858585] hover:text-[#cccccc]` pattern
- No row click interaction on DriftPage (read-only table)

### Phase 9 Backend Output Contract
The `_compute_drift` helper must return string values that match the existing `PhasePayload.drift: string` field lowercase enum values already consumed by `DashboardPage.tsx`:
- `"major"`, `"minor"`, `"none"`, `"deferred"`
- These match the existing frontend check: `p.drift === "major"` / `p.drift === "minor"` in `DashboardPage.tsx` stats computation

---

## Registry

**shadcn:** Not initialized (not applicable — Windows desktop app, no standard web component registry needed)
**Third-party registries:** None
**Registry safety gate:** Not applicable

---

## Component Inventory

Phase 9 introduces no new components. Existing components that consume `drift` field:

| Component | File | Drift Usage |
|-----------|------|------------|
| `DashboardPage` | `src/pages/DashboardPage.tsx` | Reads `p.drift === "major"` / `"minor"` for `driftLabel` stat card |
| `DriftPage` (stub) | `src/pages/DriftPage.tsx` | Will consume in Phase 10 — currently a stub |

No changes to these files are required in Phase 9.

---

## What Phase 9 Must Not Break

1. `PhasePayload.drift` remains type `string` — no type change
2. Existing `DashboardPage` drift stat card logic: `phases.some(p => p.drift === "major")` and `"minor"` checks
3. The sidebar and nav layout in `ShellLayout.tsx` — untouched by backend changes
4. Settings compatibility at `%LOCALAPPDATA%\WinGSDMonitor\settings.json`

---

## Pre-Population Sources

| Source | Decisions Used |
|--------|---------------|
| CONTEXT.md | Phase boundary (pure backend), D-01 through D-05 edge cases, `_compute_drift` signature |
| REQUIREMENTS.md | DRFT-01 logic, DRFT-04 badge color spec, DRFT-05 toggle behavior |
| ROADMAP.md | Phase 9 success criteria (4 cases), Phase 10 UI hint |
| Codebase scan | All color tokens, spacing scale, typography scale, component inventory |
| User input | 0 (all values pre-populated from upstream artifacts and codebase) |
