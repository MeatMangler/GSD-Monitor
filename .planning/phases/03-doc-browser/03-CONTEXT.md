# Phase 3: Doc Browser - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a dedicated `/docs` page to the app that lets the user navigate any file in the selected project's `.planning/` directory and read it inline as rendered markdown (or raw text for non-markdown files). Full-stack: two new backend endpoints + new React page + sidebar nav entry.

This phase touches: new `frontend/src/pages/DocsPage.tsx`, `frontend/src/App.tsx` (route), `frontend/src/ShellLayout.tsx` (nav link), `frontend/src/api.ts` (new fetch functions), and `gsd_monitor/api/app.py` (two new endpoints). No changes to existing pages.

</domain>

<decisions>
## Implementation Decisions

### Layout (DASH-05)
- **D-01:** Doc browser lives on a new `/docs` route — a dedicated full-page view, not a panel on Dashboard
- **D-02:** Page layout is a two-column split: file tree on the left (~240–280px fixed), rendered content on the right (flex-1, scrollable)
- **D-03:** "Docs" entry added to the sidebar nav in `ShellLayout.tsx`, between Dashboard and Drift

### Quick-access shortcuts (DASH-06)
- **D-04:** The 4 curated files are pinned at the top of the file tree panel in a "Quick access" section, separated from the full tree by a divider
- **D-05:** Shortcuts: ROADMAP.md, STATE.md, active PLAN.md (see D-07), REQUIREMENTS.md
- **D-06:** The same files also appear in the full tree at their actual locations — clicking either navigates to the same file
- **D-07:** Active PLAN.md shortcut = the most recent plan file for the first `in_progress` phase (resolved from `PhasePayload.artifact_paths` or by scanning `phases/{padded}/` directory). If no phase is in progress, the PLAN shortcut is omitted (not shown grayed out)

### File tree behavior (DASH-07)
- **D-08:** All files under `.planning/` are shown in the tree — not filtered to `.md` only
- **D-09:** Top-level folders (`phases/`, `codebase/`, `quick/`, etc.) are collapsed by default; files at root level are always visible
- **D-10:** On load, ROADMAP.md is auto-selected and rendered in the content pane
- **D-11:** Non-.md files (e.g., `config.json`) show raw preformatted text in the content pane when clicked

### Content rendering
- **D-12:** The content pane uses `react-markdown` + `remark-gfm` (already installed and already imported in `DashboardPage.tsx`) — same as existing plan content rendering
- **D-13:** Markdown files render as formatted HTML; all other files render as `<pre>` raw text
- **D-14:** File content is fetched on demand (clicking a file) — not pre-loaded with the tree

### Backend API
- **D-15:** Two new endpoints, following the existing `/api/quick-tasks/{planning_path:path}` URL pattern:
  - `GET /api/docs/{planning_path:path}/tree` → returns a nested JSON tree of all files/folders under the resolved planning path
  - `GET /api/docs/{planning_path:path}/file?path=relative/path` → returns raw file content as `{ "content": "..." }`
- **D-16:** Raw markdown string returned from API; `react-markdown` renders on the client — no server-side HTML generation
- **D-17:** Both endpoints must validate that the resolved file path stays within the `.planning/` directory (path traversal guard)

### Navigation state
- **D-18:** Currently-selected file tracked in local React state (not in URL) — no URL encoding of selected file path needed
- **D-19:** Switching projects (changing `selectedGroupId`) resets the selected file back to ROADMAP.md

### Claude's Discretion
- Exact panel widths and splitter behavior (fixed vs. resizable)
- Tree node expand/collapse icon style
- Whether to show file size or last-modified date in the tree
- Styling of the "Quick access" section header
- How to truncate long filenames in the tree
- Loading state for content fetch (spinner vs. skeleton)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Dashboard & Visual — DASH-05, DASH-06, DASH-07 define acceptance criteria
- `.planning/ROADMAP.md` §Phase 3 — Success criteria 1–4

### Frontend files to create/modify
- `frontend/src/pages/DocsPage.tsx` — new page (create)
- `frontend/src/App.tsx` — add `/docs` route
- `frontend/src/ShellLayout.tsx` — add "Docs" nav link; also reference the existing nav link pattern
- `frontend/src/api.ts` — add `fetchDocTree()` and `fetchDocFile()` functions + response interfaces
- `frontend/src/pages/DashboardPage.tsx` — reference for react-markdown usage pattern (lines 1–4 imports, markdown rendering in drawer)

### Backend files to modify
- `gsd_monitor/api/app.py` — add two new route handlers following the `/api/quick-tasks/{planning_path:path}` pattern (line ~231)

### Existing patterns to follow
- `frontend/src/Drawer.tsx` — existing react-markdown rendering (do NOT modify; just follow the pattern)
- `/api/quick-tasks/{planning_path:path}` in `app.py` — URL pattern for planning-path-based endpoints

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `react-markdown` + `remark-gfm` — already installed, already imported in `DashboardPage.tsx`; identical import pattern for `DocsPage.tsx`
- `SegmentPayload.planningPath` — provides the `.planning/` root path; already available in `useApp()` context via `activeSegment`
- `PhasePayload.artifact_paths` — lists phase artifact file paths; can resolve active PLAN.md from here
- `Drawer.tsx` — not reused structurally, but its markdown rendering pattern (`<ReactMarkdown remarkPlugins={[remarkGfm]}>`) is the exact pattern to copy

### Established Patterns
- Tailwind utility classes inline — `bg-[#1e1e1e]`, `bg-[#252526]`, `text-[#cccccc]`, `text-[#858585]`, `border-[#474747]`, `text-[#007acc]` for VS Code tokens
- Named function exports for pages: `export function DocsPage()`
- `useApp()` hook in page components for `activeSegment`, `activeProject`, `loading`
- Backend route pattern: `@application.get("/api/quick-tasks/{planning_path:path}")` — same pattern for `/api/docs/{planning_path:path}/tree`

### Integration Points
- `ShellLayout.tsx` nav section — add "Docs" link following the existing `<NavLink>` pattern
- `App.tsx` `<Routes>` — add `<Route path="/docs" element={<DocsPage />} />`
- `api.ts` — add two new async functions + two new response interfaces (`DocTreeNode`, `DocFileResponse`)
- `context.tsx` — no changes needed; `useApp()` already exposes `activeSegment` with `planningPath`

</code_context>

<specifics>
## Specific Ideas

- Quick-access section header label: "Quick access" (subtle, muted color)
- Active PLAN shortcut label: "PLAN (03)" or similar — include the phase number so user knows which plan it is
- The tree structure mirrors the actual filesystem layout (no reordering or flattening)
- `react-markdown` already handles GFM tables, task lists, code blocks — no additional plugins needed

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-doc-browser*
*Context gathered: 2026-04-04*
