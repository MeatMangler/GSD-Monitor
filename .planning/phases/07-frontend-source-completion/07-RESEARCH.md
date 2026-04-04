# Phase 7: Frontend Source Completion & Bundle Rebuild - Research

**Researched:** 2026-04-04
**Domain:** TypeScript / React 19 / Vite 6 — frontend source tree repair and bundle rebuild
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DASH-01 | Stats bar visible above the fold: % complete, phases done/total, active phase name | Source fix: `context.tsx` merge makes `useApp()` available; already implemented in DashboardPage.tsx |
| DASH-02 | Phase list with status colors without a click | Source fix: already implemented in DashboardPage.tsx; needs context.tsx + bundle rebuild |
| DASH-03 | Breadcrumb always visible | Source fix: already implemented in DashboardPage.tsx; needs bundle rebuild |
| DASH-04 | VS Code dark theme | Source fix: already implemented; needs bundle rebuild |
| DASH-05 | Doc browser file tree + inline markdown | Source fix: already implemented in DocsPage.tsx; needs bundle rebuild |
| DASH-06 | ROADMAP/STATE/PLAN/REQUIREMENTS quick-access | Source fix: already implemented in DocsPage.tsx; needs bundle rebuild |
| DASH-07 | Any `.planning/` file navigable and renderable | Source fix: already implemented in DocsPage.tsx; needs bundle rebuild |
| PERF-03 | stateCurrentPosition populated and displayed on dashboard | Source fix: `stateCurrentPosition` field is in master api.ts + DashboardPage.tsx; needs bundle rebuild |
| PERF-04 | SettingsPage.save() no reload() call | Source fix: SettingsPage.tsx must be merged from worktree; already implements correct behavior |
</phase_requirements>

---

## Summary

Phase 7 is a **source tree repair and rebuild phase**, not a feature implementation phase. All nine listed requirements (DASH-01 through DASH-07, PERF-03, PERF-04) are already fully implemented in the correct source files — they just cannot be compiled or served because five required files are absent from the master branch working tree, and the `frontend/dist/` bundle predates all Phase 02-05 frontend changes.

The core problem has two parts. First, the frontend source tree on master is missing five files: `context.tsx` (never merged from `worktree-agent-a9b06372`), `SettingsPage.tsx` (same), `DriftPage.tsx`, `QuickTasksPage.tsx`, and `VerificationPage.tsx` (never committed anywhere). Without these files `tsc -b` fails immediately on unresolved imports in `App.tsx`, `ShellLayout.tsx`, and `DashboardPage.tsx`. Second, even with correct source, the existing `frontend/dist/` bundle (built 2026-04-03 20:07) predates DocsPage, stateCurrentPosition, AppProvider/context, and ReactMarkdown — it serves the pre-Phase-02 DashboardPage.

One additional complication: `DashboardPage.tsx` imports `../Drawer` (a slide-over component), but `Drawer.tsx` has **never been committed to any git branch** and is **not present on disk**. The Phase 02 research and UI-SPEC documents treat it as a pre-existing file ("unchanged per D-08"), but it never made it into git. This must be created as part of Phase 7 for `tsc -b` to pass.

A further concern: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, and `frontend/index.html` are **not tracked in git and do not exist on disk**. The `node_modules/` directory is present (containing vite 6.4.1, tsc 5.9.3, react 19, etc.), meaning a previous install was done from a package.json that subsequently disappeared. Phase 7 must reconstruct these config files before `npm run build` can be executed.

**Primary recommendation:** Merge `context.tsx` + `SettingsPage.tsx` from `worktree-agent-a9b06372`, create stub pages for Drift/QuickTasks/Verification, create `Drawer.tsx`, reconstruct the missing config files (`package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`), run `tsc -b` to zero errors, run `npm run build` to produce a fresh bundle.

---

## Standard Stack

### Core (all already installed in node_modules)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vite | 6.4.1 | Build tooling + dev server | Confirmed in `node_modules/.bin/vite --version` |
| TypeScript | 5.9.3 | Type checker (`tsc -b`) | Confirmed in `node_modules/.bin/tsc --version` |
| React | 19.0 | UI framework | CLAUDE.md constraint; installed |
| react-router-dom | 7.0 | Client-side routing | Already in App.tsx |
| Tailwind CSS | 4.0 | Utility styling via `@tailwindcss/vite` | CLAUDE.md constraint; installed |
| react-markdown | 10.0 | Markdown rendering | Already used in DashboardPage.tsx, DocsPage.tsx |
| remark-gfm | 4.0 | GFM tables/strikethrough | Already used alongside react-markdown |

### Config Files That Must Be Reconstructed

| File | Status | What It Must Contain |
|------|--------|----------------------|
| `frontend/package.json` | NOT ON DISK, NOT IN GIT | `name: gsd-monitor-ui`, scripts (`dev`, `build`), all dependencies |
| `frontend/tsconfig.json` | NOT ON DISK, NOT IN GIT | strict mode, ES2022 target, bundler moduleResolution, path alias `@/*` |
| `frontend/vite.config.ts` | NOT ON DISK, NOT IN GIT | `@tailwindcss/vite` plugin, `@vitejs/plugin-react`, dev proxy `/api` + `/ws` |
| `frontend/index.html` | NOT ON DISK, NOT IN GIT | Entry HTML referencing `/src/main.tsx` |

**How to reconstruct:** CLAUDE.md documents all versions and configuration precisely. The lock file at `frontend/node_modules/.package-lock.json` confirms `name: gsd-monitor-ui`. All config file content can be derived from CLAUDE.md + the installed node_modules state.

**Installation:** No new `npm install` needed. All packages are already in `node_modules/`. Reconstruct config files only.

---

## Architecture Patterns

### Exact Source Files Needed

**Files to git-checkout from `worktree-agent-a9b06372`:**

| File | Branch Source | How to Get It |
|------|--------------|---------------|
| `frontend/src/context.tsx` | `worktree-agent-a9b06372` commit `5a0fcaf7` | `git checkout worktree-agent-a9b06372 -- frontend/src/context.tsx` |
| `frontend/src/pages/SettingsPage.tsx` | `worktree-agent-a9b06372` commit `5a0fcaf7` | `git checkout worktree-agent-a9b06372 -- frontend/src/pages/SettingsPage.tsx` |

**CRITICAL:** Do NOT use `git merge` — the worktree branch contains older versions of `api.ts` and `DashboardPage.tsx` (it lacks `stateCurrentPosition`). Cherry-pick only the two files above.

**Files to create as new stubs (never existed in any branch):**

| File | Requirement | Stub Content |
|------|-------------|--------------|
| `frontend/src/pages/DriftPage.tsx` | App.tsx routing | Minimal placeholder: `export function DriftPage() { return <div className="p-8 text-[#858585]">Drift detection coming in v2.</div>; }` |
| `frontend/src/pages/QuickTasksPage.tsx` | App.tsx routing | Minimal placeholder |
| `frontend/src/pages/VerificationPage.tsx` | App.tsx routing | Minimal placeholder |

**File to create (never committed, referenced by DashboardPage.tsx):**

| File | What It Is | What It Must Export |
|------|-----------|---------------------|
| `frontend/src/Drawer.tsx` | Side-drawer component for phase detail panel | `export function Drawer({ open, onClose, title, children })` |

The `Drawer` component props are determinable from `DashboardPage.tsx` usage:
```typescript
<Drawer
  open={drawerOpen}
  onClose={() => setDrawerOpen(false)}
  title={selected ? `${String(selected.number).padStart(2, "0")} — ${selected.title}` : "Phase"}
>
  {selected && (...)}
</Drawer>
```

It needs: `open: boolean`, `onClose: () => void`, `title: string`, `children: ReactNode`. It is a VS Code dark-themed slide-over panel.

### Stub Component Pattern

```typescript
// Source: project convention — named export, no default export
import type { ReactNode } from "react";

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children?: ReactNode;
}

export function Drawer({ open, onClose, title, children }: DrawerProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <aside className="relative flex w-[480px] flex-col border-l border-[#474747] bg-[#1e1e1e] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-[#474747] px-4 py-3">
          <h2 className="font-mono text-sm font-medium text-[#cccccc]">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-[#858585] hover:text-[#cccccc]"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 text-sm text-[#cccccc]">
          {children}
        </div>
      </aside>
    </div>
  );
}
```

### Config File Reconstruction (package.json)

Based on CLAUDE.md and installed node_modules:

```json
{
  "name": "gsd-monitor-ui",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0",
    "react-markdown": "^10.0.0",
    "remark-gfm": "^4.0.0"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^5.0.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.9.0",
    "vite": "^6.0.0"
  }
}
```

### Config File Reconstruction (vite.config.ts)

```typescript
// Source: CLAUDE.md — @tailwindcss/vite plugin, dev proxy /api + /ws
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8765",
      "/ws": { target: "ws://127.0.0.1:8765", ws: true },
    },
  },
});
```

### Config File Reconstruction (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "noEmit": true,
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"]
}
```

### Config File Reconstruction (index.html)

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>GSD Monitor</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### Anti-Patterns to Avoid

- **Do NOT `git merge worktree-agent-a9b06372`:** That branch contains older api.ts (missing `stateCurrentPosition`) and older DashboardPage.tsx. A merge would overwrite Phase 4/5 work.
- **Do NOT `npm install`:** All packages are installed. Adding a package.json and running `npm install` in an already-populated node_modules will regenerate the lock file and may change versions.
- **Do NOT modify App.tsx:** The routing is already correct. The goal is to make the imported files exist.
- **Do NOT add `@tailwindcss/typography` for prose support:** The installed packages do not include it; `prose prose-invert` classes are currently used in DashboardPage and DocsPage. If they render correctly from the current bundle (they appear to), the typography plugin is already installed. Verify before assuming it's missing.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown rendering in Drawer | Custom markdown parser | `react-markdown` + `remark-gfm` (already installed) | Matches existing DashboardPage.tsx + DocsPage.tsx pattern |
| Overlay/backdrop for Drawer | JS-based modal system | CSS fixed positioning + bg-black/50 | Sufficient for this simple use case; consistent with existing patterns |
| TypeScript compilation | Manual transpilation | `tsc -b` command | Already in `node_modules/.bin/tsc` |
| Build bundling | Webpack/Rollup | `npm run build` via Vite | Already set up in node_modules |

---

## Common Pitfalls

### Pitfall 1: Merging the wrong branch files
**What goes wrong:** `git merge worktree-agent-a9b06372` brings in `api.ts` without `stateCurrentPosition` and `DashboardPage.tsx` without the state-aware breadcrumb — silently reverting Phase 4/5 work.
**Why it happens:** The worktree branch diverged at commit `7135fe0` (Phase 4 docs only) and never received Phase 4/5 frontend changes that landed on master.
**How to avoid:** Use `git checkout worktree-agent-a9b06372 -- frontend/src/context.tsx frontend/src/pages/SettingsPage.tsx` to cherry-pick only the two missing files. Then verify no other files were touched.
**Warning signs:** After checkout, `git diff HEAD -- frontend/src/api.ts` shows stateCurrentPosition removed.

### Pitfall 2: Missing package.json blocks tsc and build
**What goes wrong:** Running `tsc -b` or `npm run build` fails with "no tsconfig.json found" or "package.json not found" because the config files do not exist on disk.
**Why it happens:** These files were never committed to git and are not present on the working tree.
**How to avoid:** Create all four config files (`package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`) in `frontend/` before attempting any build step.
**Warning signs:** `ls frontend/` shows only `src/`, `dist/`, `node_modules/`, `.vite/` — no config files.

### Pitfall 3: Drawer.tsx missing causes tsc failure
**What goes wrong:** `tsc -b` reports "Cannot find module '../Drawer'" because `Drawer.tsx` was referenced in `DashboardPage.tsx` from Phase 02 but never committed.
**Why it happens:** The Phase 02 plan treated Drawer as pre-existing ("unchanged per D-08"), but it was part of the pre-git scaffold that was never tracked.
**How to avoid:** Create `frontend/src/Drawer.tsx` with the correct component interface before running `tsc -b`.
**Warning signs:** DashboardPage.tsx line 5 imports `../Drawer` but `ls frontend/src/` shows no `Drawer.tsx`.

### Pitfall 4: @tailwindcss/typography missing
**What goes wrong:** `prose prose-invert` Tailwind classes in DashboardPage/DocsPage render with no styling if the typography plugin is not installed.
**Why it happens:** Tailwind v4 requires `@tailwindcss/typography` as an explicit plugin for `prose` class support.
**How to avoid:** Check `ls node_modules/@tailwindcss/` — if `typography` is absent, either add it to package.json and install, or remove `prose` class usage (replacing with explicit text styles). The existing bundle was built at 20:07 before DocsPage existed, so prose rendering in DocsPage has never been tested in a bundle.
**Warning signs:** After `npm run build`, opening the app shows DocsPage markdown without any typography formatting.

### Pitfall 5: main.tsx missing
**What goes wrong:** Vite build fails because `index.html` references `/src/main.tsx` but that file may not exist.
**Why it happens:** `main.tsx` was likely part of the pre-git scaffold, same as the config files.
**How to avoid:** Check `ls frontend/src/` before building — if `main.tsx` is absent, create it with standard React 19 `createRoot` pattern.
**Warning signs:** Vite build error "Could not resolve src/main.tsx".

---

## Runtime State Inventory

This phase involves no renaming or data migration. Skip.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | npm, Vite, tsc | ✓ | 22.16.0 | — |
| npm | Package scripts | ✓ | 11.11.1 | — |
| Vite CLI | `npm run build` | ✓ | 6.4.1 (in node_modules) | Run `./node_modules/.bin/vite build` |
| tsc CLI | `tsc -b` | ✓ | 5.9.3 (in node_modules) | Run `./node_modules/.bin/tsc -b` |
| React 19 | UI framework | ✓ | 19.x (in node_modules) | — |
| react-markdown | Markdown rendering | ✓ | 10.x (in node_modules) | — |
| `frontend/package.json` | `npm run build` | ✗ | — | Must create from CLAUDE.md spec |
| `frontend/tsconfig.json` | `tsc -b` | ✗ | — | Must create from CLAUDE.md spec |
| `frontend/vite.config.ts` | Vite build | ✗ | — | Must create from CLAUDE.md spec |
| `frontend/index.html` | Vite entry point | ✗ | — | Must create |
| `frontend/src/main.tsx` | Vite entry point | unknown | — | Create if absent |

**Missing dependencies with no fallback:** None — all missing items can be created from spec.

**Missing dependencies requiring creation:**
- `frontend/package.json` — create first; `npm run build` reads it for script definition
- `frontend/tsconfig.json` — create before `tsc -b`
- `frontend/vite.config.ts` — create before Vite build
- `frontend/index.html` — create before Vite build

---

## Validation Architecture

> `workflow.nyquist_validation` is `false` in `.planning/config.json`. This section is SKIPPED.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tailwind v3 (`tailwind.config.js`) | Tailwind v4 (`@tailwindcss/vite` plugin, no config file) | v4.0.0 | No `tailwind.config.js` needed; import via CSS `@import "tailwindcss"` |
| `@on_event` FastAPI | `lifespan` context manager | Phase 06 | Already done in backend; no frontend impact |
| Old dist bundle (pre-Phase 02) | Fresh bundle with all Phase 02-05 features | This phase | Users finally see redesigned UI |

---

## Open Questions

1. **Is `@tailwindcss/typography` installed?**
   - What we know: `prose prose-invert prose-sm` classes are used in DocsPage.tsx and DashboardPage.tsx. The existing bundle was built before DocsPage existed.
   - What's unclear: Whether the typography plugin is in node_modules.
   - Recommendation: `ls frontend/node_modules/@tailwindcss/` before building. If `typography/` is absent, the plan must either add it (`npm install @tailwindcss/typography`) or remove `prose` class usage.

2. **Does `frontend/src/main.tsx` exist?**
   - What we know: It is not tracked in git (`git ls-files frontend/src/` shows only App.tsx, ShellLayout.tsx, api.ts, index.css, pages/). Index.html (once created) will reference it.
   - What's unclear: Whether it exists as an untracked file on disk.
   - Recommendation: `ls frontend/src/` — if `main.tsx` is absent, create it with `createRoot(document.getElementById("root")!).render(<BrowserRouter><App /></BrowserRouter>)` pattern.

3. **Does tsconfig.json need `"references"` for `tsc -b` project references mode?**
   - What we know: `tsc -b` is specified in success criteria (not `tsc --noEmit`). The `-b` flag builds project references. For a single-project setup, `tsc -b` with a plain tsconfig.json that has `"noEmit": true` works fine.
   - What's unclear: Whether a `tsconfig.node.json` for vite.config.ts is needed.
   - Recommendation: Start with a single `tsconfig.json`. Add `tsconfig.node.json` only if `tsc -b` errors on vite.config.ts import resolution.

---

## Sources

### Primary (HIGH confidence)
- Direct source inspection: `git show worktree-agent-a9b06372:frontend/src/context.tsx` — confirmed full file content
- Direct source inspection: `git show worktree-agent-a9b06372:frontend/src/pages/SettingsPage.tsx` — confirmed full file content
- Direct source inspection: `frontend/src/App.tsx`, `DashboardPage.tsx`, `ShellLayout.tsx` — confirmed all imports
- `frontend/node_modules/.package-lock.json` — confirmed `name: gsd-monitor-ui`, all installed versions
- `frontend/node_modules/.bin/vite --version` → 6.4.1, `tsc --version` → 5.9.3
- CLAUDE.md Technology Stack section — versions, config file specs, Tailwind v4 pattern

### Secondary (MEDIUM confidence)
- `.planning/phases/02-visual-redesign/02-RESEARCH.md` — confirms Drawer.tsx was a pre-existing file not to be touched
- `.planning/phases/03-doc-browser/03-CONTEXT.md` — confirms Drawer.tsx pattern and its role

### Tertiary (LOW confidence — not yet verified by build)
- Tailwind v4 `@tailwindcss/vite` config — based on CLAUDE.md description; not verified by test build

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages confirmed installed in node_modules with exact versions
- Architecture (source files): HIGH — exact file contents confirmed by git inspection
- Config reconstruction: MEDIUM — based on CLAUDE.md spec + lock file; not verified by actual build yet
- Pitfalls: HIGH — all identified directly from code inspection, not inference

**Research date:** 2026-04-04
**Valid until:** Stable (no moving parts — this is a deterministic repair phase)

---

## Summary of Work Needed

| Task | Source | Action |
|------|--------|--------|
| Reconstruct `frontend/package.json` | CLAUDE.md + lock file | Create new file |
| Reconstruct `frontend/tsconfig.json` | CLAUDE.md | Create new file |
| Reconstruct `frontend/vite.config.ts` | CLAUDE.md | Create new file |
| Reconstruct `frontend/index.html` | Standard Vite template | Create new file |
| Check/create `frontend/src/main.tsx` | Standard React 19 pattern | Create if absent |
| Add `frontend/src/context.tsx` | `worktree-agent-a9b06372` | `git checkout` single file |
| Add `frontend/src/pages/SettingsPage.tsx` | `worktree-agent-a9b06372` | `git checkout` single file |
| Create `frontend/src/Drawer.tsx` | Never existed in git | Create new component |
| Create `frontend/src/pages/DriftPage.tsx` | Never existed | Placeholder stub |
| Create `frontend/src/pages/QuickTasksPage.tsx` | Never existed | Placeholder stub |
| Create `frontend/src/pages/VerificationPage.tsx` | Never existed | Placeholder stub |
| Verify `tsc -b` passes | — | Confirm zero errors |
| Run `npm run build` | — | Produce fresh dist bundle |
| Verify bundle contents | — | grep for DocsPage, AppProvider, stateCurrentPosition, ReactMarkdown |
