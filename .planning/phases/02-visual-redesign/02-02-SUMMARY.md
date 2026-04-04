---
phase: 02-visual-redesign
plan: 02
subsystem: frontend
tags: [ui, theme, tailwind, vscode-tokens, shell-layout]
dependency_graph:
  requires: [02-01]
  provides: [shell-layout-vscode-theme]
  affects: [frontend/src/ShellLayout.tsx]
tech_stack:
  added: []
  patterns: [tailwind-arbitrary-hex-values]
key_files:
  modified:
    - frontend/src/ShellLayout.tsx
decisions:
  - VS Code hex tokens applied as Tailwind arbitrary values (bg-[#hex]) — no tailwind.config.js needed in v4
  - NavLink active state uses bg-[#2a2d2e] text-[#cccccc] — no left border (phase rows only)
  - text-red-400 preserved for error display per UI-SPEC semantic color contract
metrics:
  duration: ~2 min
  completed: 2026-04-04
  tasks_completed: 1
  files_changed: 1
---

# Phase 02 Plan 02: ShellLayout VS Code Token Migration Summary

**One-liner:** Replaced all zinc-scale Tailwind classes in ShellLayout.tsx with VS Code Dark+ hex tokens using Tailwind v4 arbitrary value syntax.

## What Was Done

Executed a mechanical class-string replacement across `frontend/src/ShellLayout.tsx`, converting every zinc-scale color class to its VS Code Dark+ hex equivalent. No JSX structure, event handlers, or logic was changed — only `className` attribute values.

### Token Swaps Applied

| Element | Before | After |
|---------|--------|-------|
| Outer wrapper div | `bg-zinc-950` | `bg-[#1e1e1e]` |
| Aside sidebar | `bg-zinc-900/80` | `bg-[#252526]` |
| Aside border | `border-zinc-800` | `border-[#474747]` |
| Header border | `border-zinc-800` | `border-[#474747]` |
| App title h1 | `text-zinc-100` | `text-[#cccccc]` |
| Subtitle p | `text-zinc-500` | `text-[#858585]` |
| Loading text | `text-zinc-500` | `text-[#858585]` |
| All labels | `text-zinc-400` | `text-[#858585]` |
| Select borders | `border-zinc-700` | `border-[#474747]` |
| Select backgrounds | `bg-zinc-950` | `bg-[#252526]` |
| Worktree badge | `bg-zinc-700 text-zinc-300` | `bg-[#2a2d2e] text-[#858585]` |
| Tooltip container | `bg-zinc-900 border-zinc-700` | `bg-[#252526] border-[#474747]` |
| Tooltip branch | `text-zinc-300` | `text-[#cccccc]` |
| Tooltip path | `text-zinc-500` | `text-[#858585]` |
| Tooltip "main" | `text-zinc-600` | `text-[#858585]` |
| NavLink active | `bg-zinc-800 text-white` | `bg-[#2a2d2e] text-[#cccccc]` |
| NavLink inactive | `text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200` | `text-[#858585] hover:bg-[#2a2d2e] hover:text-[#cccccc]` |

## Verification

- TypeScript: `npx tsc -b --noEmit` — zero errors
- Vite build: `npx vite build` — succeeded (302 modules, 3.34s)
- Pattern check: zero zinc-scale color classes remain in ShellLayout.tsx
- `text-red-400` preserved for error display

## Commits

| Task | Description | Hash |
|------|-------------|------|
| 1 | Swap all zinc-scale color classes to VS Code Dark+ hex tokens | 09c0e51 |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all class replacements are complete and functional. No data stubs or placeholder text introduced.

## Self-Check: PASSED

- File `frontend/src/ShellLayout.tsx` exists and contains all required VS Code hex tokens
- Commit `09c0e51` verified in git log
- Zero zinc-scale color classes remain
- `text-red-400` preserved
