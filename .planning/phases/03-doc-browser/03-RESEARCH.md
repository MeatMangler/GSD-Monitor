# Phase 3: Doc Browser - Research

**Researched:** 2026-04-04
**Domain:** FastAPI path endpoints + React two-pane file browser + react-markdown rendering
**Confidence:** HIGH

## Summary

Phase 3 adds a `/docs` route backed by two new FastAPI endpoints. The entire implementation builds on patterns and libraries that are already present and validated in the codebase — `react-markdown`, `remark-gfm`, `NavLink`, `useApp()`, and the `/api/quick-tasks/{planning_path:path}` URL pattern. No new dependencies are needed.

The most technically sensitive parts are (1) the path-traversal guard on the backend (resolved `file` path must remain within the `planning_path` root), and (2) the active PLAN.md resolution logic on the frontend (filter `PhasePayload.artifact_paths` to `-PLAN.md` suffixes for the first `in_progress` phase). Both are straightforward once the patterns are clear.

The two-column page layout (fixed-width tree, flex-1 scrollable content) is a standard Tailwind pattern with no special dependencies. Tree expand/collapse uses local React state. File content is fetched on demand.

**Primary recommendation:** Implement all backend logic in `app.py` following the `quick-tasks` URL pattern. Implement all frontend logic in `DocsPage.tsx` with local state only. Do not touch `context.tsx`.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Layout (DASH-05)**
- D-01: Doc browser lives on a new `/docs` route — a dedicated full-page view, not a panel on Dashboard
- D-02: Page layout is a two-column split: file tree on the left (~240-280px fixed), rendered content on the right (flex-1, scrollable)
- D-03: "Docs" entry added to the sidebar nav in `ShellLayout.tsx`, between Dashboard and Drift

**Quick-access shortcuts (DASH-06)**
- D-04: The 4 curated files are pinned at the top of the file tree panel in a "Quick access" section, separated from the full tree by a divider
- D-05: Shortcuts: ROADMAP.md, STATE.md, active PLAN.md (see D-07), REQUIREMENTS.md
- D-06: The same files also appear in the full tree at their actual locations — clicking either navigates to the same file
- D-07: Active PLAN.md shortcut = the most recent plan file for the first `in_progress` phase (resolved from `PhasePayload.artifact_paths` or by scanning `phases/{padded}/` directory). If no phase is in progress, the PLAN shortcut is omitted (not shown grayed out)

**File tree behavior (DASH-07)**
- D-08: All files under `.planning/` are shown in the tree — not filtered to `.md` only
- D-09: Top-level folders (`phases/`, `codebase/`, `quick/`, etc.) are collapsed by default; files at root level are always visible
- D-10: On load, ROADMAP.md is auto-selected and rendered in the content pane
- D-11: Non-.md files (e.g., `config.json`) show raw preformatted text in the content pane when clicked

**Content rendering**
- D-12: The content pane uses `react-markdown` + `remark-gfm` (already installed and already imported in `DashboardPage.tsx`) — same as existing plan content rendering
- D-13: Markdown files render as formatted HTML; all other files render as `<pre>` raw text
- D-14: File content is fetched on demand (clicking a file) — not pre-loaded with the tree

**Backend API**
- D-15: Two new endpoints, following the existing `/api/quick-tasks/{planning_path:path}` URL pattern:
  - `GET /api/docs/{planning_path:path}/tree` — returns a nested JSON tree of all files/folders under the resolved planning path
  - `GET /api/docs/{planning_path:path}/file?path=relative/path` — returns raw file content as `{ "content": "..." }`
- D-16: Raw markdown string returned from API; `react-markdown` renders on the client — no server-side HTML generation
- D-17: Both endpoints must validate that the resolved file path stays within the `.planning/` directory (path traversal guard)

**Navigation state**
- D-18: Currently-selected file tracked in local React state (not in URL) — no URL encoding of selected file path needed
- D-19: Switching projects (changing `selectedGroupId`) resets the selected file back to ROADMAP.md

### Claude's Discretion
- Exact panel widths and splitter behavior (fixed vs. resizable)
- Tree node expand/collapse icon style
- Whether to show file size or last-modified date in the tree
- Styling of the "Quick access" section header
- How to truncate long filenames in the tree
- Loading state for content fetch (spinner vs. skeleton)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DASH-05 | Doc browser panel shows `.planning/` file tree and renders selected markdown inline | Two-column layout pattern documented; tree state via local useState; markdown rendering via existing react-markdown |
| DASH-06 | ROADMAP.md, STATE.md, active PLAN.md, and REQUIREMENTS.md are surfaced as default quick-access files | Active PLAN.md resolution from `artifact_paths` documented; quick-access section above divider |
| DASH-07 | Any file in `.planning/` is navigable and renderable in the doc browser | Backend tree endpoint + on-demand file fetch pattern documented; path traversal guard pattern documented |
</phase_requirements>

---

## Project Constraints (from CLAUDE.md)

- Tech stack locked: Python 3.11+ / FastAPI / pywebview / React 19 / Tailwind CSS v4 / Vite 6 — no stack changes
- Windows only (Edge WebView2)
- App is read-only — never writes to project files
- Settings format: `%LOCALAPPDATA%\WinGSDMonitor\settings.json` PascalCase — not relevant to this phase
- Named exports only for React pages/components
- Function components exclusively — no class components
- Tailwind utility classes inline — no CSS modules or styled components
- VS Code dark hex tokens via arbitrary values (`bg-[#1e1e1e]`, `bg-[#252526]`, `text-[#cccccc]`, etc.)
- `useApp()` hook for shared state; local `useState` for page-level UI
- `from __future__ import annotations` at top of every Python module
- Type hints on all function signatures
- `PascalCase.tsx` for component files; `camelCase.ts` for non-component modules
- `snake_case` for Python modules and functions
- No default exports for pages (App.tsx is the one exception)

---

## Standard Stack

### Core (all already installed — no new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react-markdown | 10.0 | Render markdown string as formatted HTML | Already installed; used in DashboardPage.tsx / Drawer.tsx |
| remark-gfm | 4.0 | GFM tables, task lists, strikethrough | Already installed; paired with react-markdown |
| react-router-dom | 7.0 | `/docs` route and `NavLink` active state | Already powering all existing routes |
| Tailwind CSS v4 | 4.0 | Two-column layout, tree item styling | Project-standard; arbitrary hex values for VS Code theme |
| FastAPI | >=0.115.0 | Two new GET endpoints | Project-standard; existing `path` param pattern reused |

### No New Dependencies Required

All libraries needed for this phase are already in `package.json` and `pyproject.toml`. No `npm install` or `pip install` steps are needed.

---

## Architecture Patterns

### Recommended Project Structure Changes

```
frontend/src/
├── pages/
│   ├── DocsPage.tsx          # NEW — two-column doc browser page
│   └── DashboardPage.tsx     # unchanged
├── App.tsx                   # ADD /docs route
├── ShellLayout.tsx           # ADD "Docs" nav entry between Dashboard and Drift
└── api.ts                    # ADD fetchDocTree(), fetchDocFile(), DocTreeNode, DocFileResponse

gsd_monitor/api/
└── app.py                    # ADD two route handlers before WebSocket handler
```

### Pattern 1: Backend — Path-Based Endpoints

The existing `quick-tasks` endpoint is the exact template. Both new endpoints follow the same structure: accept `planning_path` as a path parameter, `unquote()` it, validate it exists, return JSON.

```python
# Source: gsd_monitor/api/app.py line 231 (existing pattern)
@application.get("/api/quick-tasks/{planning_path:path}")
async def quick_tasks(planning_path: str) -> dict[str, Any]:
    from urllib.parse import unquote
    p = unquote(planning_path)
    tasks = QuickTaskParser.parse(p)
    return {"tasks": [t.model_dump(mode="json") for t in tasks]}
```

New endpoints follow the same shape:

```python
# Pattern for tree endpoint
@application.get("/api/docs/{planning_path:path}/tree")
async def docs_tree(planning_path: str) -> dict[str, Any]:
    from urllib.parse import unquote
    root = Path(unquote(planning_path)).resolve()
    # ... build and return tree
    return {"tree": [...]}

# Pattern for file endpoint — note: query param, not path segment
@application.get("/api/docs/{planning_path:path}/file")
async def docs_file(planning_path: str, path: str) -> dict[str, Any]:
    from urllib.parse import unquote
    root = Path(unquote(planning_path)).resolve()
    # ... validate and read
    return {"content": "..."}
```

**Important:** The `/tree` and `/file` suffixes are literal path segments AFTER the `planning_path:path` capture. FastAPI handles this correctly because it matches the full route pattern including the suffix.

### Pattern 2: Path Traversal Guard

Per D-17, both endpoints must confirm the resolved file path stays within the planning root. Python's `Path.resolve()` followed by checking `root in file_path.parents` (or `str(file_path).startswith(str(root))`) is the standard approach.

```python
# Canonical path traversal guard pattern
root = Path(unquote(planning_path)).resolve()
if not root.is_dir():
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="planning path not found")
target = (root / rel_path).resolve()
# Must be inside root — reject anything that escapes via ../
if root not in target.parents and target != root:
    from fastapi import HTTPException
    raise HTTPException(status_code=403, detail="path outside planning directory")
```

### Pattern 3: Tree JSON Structure

The tree endpoint returns a recursive node structure. A flat list of nodes with `type`, `name`, `path` (relative to planning root), and `children` (for directories) is sufficient and easy to render in React.

```python
# Tree node shape
{
  "name": "phases",
  "path": "phases",       # relative to planning root
  "type": "dir",
  "children": [
    {
      "name": "01-worktree-deduplication",
      "path": "phases/01-worktree-deduplication",
      "type": "dir",
      "children": [...]
    }
  ]
}
# Root-level files
{
  "name": "ROADMAP.md",
  "path": "ROADMAP.md",
  "type": "file",
  "children": []
}
```

Build with `Path.iterdir()` recursively, sorting dirs before files within each level (or alphabetically). Use `sorted()` with `key=lambda p: (p.is_file(), p.name.lower())`.

### Pattern 4: Frontend — Two-Column Layout

```tsx
// DocsPage.tsx skeleton
export function DocsPage() {
  const { activeSegment, activeProject, loading } = useApp();
  const [tree, setTree] = useState<DocTreeNode[]>([]);
  const [selectedPath, setSelectedPath] = useState<string>("ROADMAP.md");
  const [content, setContent] = useState<string>("");
  const [contentLoading, setContentLoading] = useState(false);
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());

  // Reset to ROADMAP.md when project changes (D-19)
  useEffect(() => {
    setSelectedPath("ROADMAP.md");
  }, [activeSegment?.planningPath]);

  // Fetch tree when segment changes
  useEffect(() => {
    if (!activeSegment?.planningPath) return;
    void fetchDocTree(activeSegment.planningPath).then(setTree).catch(() => setTree([]));
  }, [activeSegment?.planningPath]);

  // Fetch file content on selection (D-14)
  useEffect(() => {
    if (!activeSegment?.planningPath || !selectedPath) return;
    setContentLoading(true);
    void fetchDocFile(activeSegment.planningPath, selectedPath)
      .then((r) => setContent(r.content))
      .catch(() => setContent(""))
      .finally(() => setContentLoading(false));
  }, [activeSegment?.planningPath, selectedPath]);

  return (
    <div className="flex h-full">
      {/* Tree panel ~260px fixed */}
      <aside className="w-[260px] shrink-0 border-r border-[#474747] overflow-auto">
        {/* Quick access section (D-04, D-05) */}
        {/* Full tree (D-08, D-09) */}
      </aside>
      {/* Content pane */}
      <main className="flex-1 overflow-auto p-6">
        {/* ReactMarkdown or <pre> based on file extension (D-12, D-13) */}
      </main>
    </div>
  );
}
```

### Pattern 5: Markdown vs Raw Rendering (D-12, D-13)

```tsx
// Source: DashboardPage.tsx lines 178-179 / Drawer.tsx
const isMd = selectedPath.endsWith(".md");

{isMd ? (
  <div className="prose prose-invert prose-sm max-w-none">
    <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
  </div>
) : (
  <pre className="text-sm text-[#cccccc] whitespace-pre-wrap">{content}</pre>
)}
```

### Pattern 6: Active PLAN.md Resolution (D-07)

`PhasePayload.artifact_paths` contains absolute paths to `*-PLAN.md` and `*-SUMMARY.md` files for each phase. The active PLAN is resolved client-side:

```ts
// In DocsPage.tsx — derive activePlanPath from activeProject
const activePlanPath = useMemo(() => {
  if (!activeProject || !activeSegment) return null;
  const phases = activeProject.milestones.flatMap((m) => m.phases);
  const inProgress = phases.find((p) => p.status === "in_progress");
  if (!inProgress) return null;
  const planArtifact = inProgress.artifact_paths
    .filter((p) => p.endsWith("-PLAN.md"))
    .sort()
    .at(-1);  // most recent by filename sort
  if (!planArtifact) return null;
  // Convert absolute path to relative path from planningPath root
  const root = activeSegment.planningPath;
  return planArtifact.startsWith(root)
    ? planArtifact.slice(root.length).replace(/^[/\\]+/, "").replace(/\\/g, "/")
    : null;
}, [activeProject, activeSegment]);
```

**Label:** CONTEXT.md decision says "PLAN (03)" style. Derive the phase number from `inProgress.number` and format as `PLAN (${String(inProgress.number).padStart(2, "0")})`.

### Pattern 7: NavLink Integration (ShellLayout.tsx)

The `nav` array on line 6 of `ShellLayout.tsx` drives the sidebar. Insert `{ to: "/docs", label: "Docs" }` between `"/dashboard"` and `"/drift"`:

```ts
// Source: ShellLayout.tsx lines 6-12
const nav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/docs", label: "Docs" },        // INSERT HERE
  { to: "/drift", label: "Drift" },
  { to: "/quick-tasks", label: "Quick Tasks" },
  { to: "/verification", label: "Verification" },
  { to: "/settings", label: "Settings" },
];
```

### Pattern 8: api.ts Additions

```ts
// Two new interfaces
export interface DocTreeNode {
  name: string;
  path: string;   // relative to planning root, forward slashes
  type: "file" | "dir";
  children: DocTreeNode[];
}

export interface DocFileResponse {
  content: string;
}

// Two new fetch functions
export async function fetchDocTree(planningPath: string): Promise<DocTreeNode[]> {
  const enc = encodeURIComponent(planningPath);
  const r = await fetch(`${base}/api/docs/${enc}/tree`, noStore);
  if (!r.ok) throw new Error(await r.text());
  const j = await r.json();
  return j.tree ?? [];
}

export async function fetchDocFile(planningPath: string, relPath: string): Promise<DocFileResponse> {
  const enc = encodeURIComponent(planningPath);
  const params = new URLSearchParams({ path: relPath });
  const r = await fetch(`${base}/api/docs/${enc}/file?${params}`, noStore);
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<DocFileResponse>;
}
```

### Anti-Patterns to Avoid

- **Using `planningPath` as a URL segment without encoding:** The path contains Windows drive letters and backslashes (`D:\foo\bar`). Always `encodeURIComponent()` on the frontend; always `unquote()` on the backend.
- **Storing selected file in URL:** D-18 explicitly forbids this. Keep in local React state only.
- **Pre-loading all file contents with the tree:** D-14 requires on-demand fetch only. Loading the full tree is enough.
- **Skipping the path traversal guard:** Any `?path=` query parameter from the client must be resolved and validated server-side before reading. A user sending `?path=../../sensitive` must be rejected.
- **Using `prose` typography without `prose-invert`:** The app uses a dark background. Without `prose-invert`, text will render dark-on-dark. Always use `prose prose-invert prose-sm max-w-none` (same as Drawer.tsx).
- **Collapsing all directories including root-level files:** D-09 says top-level FOLDERS collapse by default, but root-level FILES are always visible. The tree renders root files directly; only subdirectory nodes start collapsed.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown rendering | Custom HTML converter | `react-markdown` + `remark-gfm` | Already installed; handles GFM tables, task lists, fenced code, etc. |
| File tree UI library | External tree component | Local `useState` + recursive render | No new dependency needed; tree is simple enough for inline recursion |
| Path encoding | Custom URL escaping | `encodeURIComponent()` / `URLSearchParams` | Standard Web API; handles all edge cases including Windows paths |
| Path traversal protection | Regex on path string | `Path.resolve()` + parent check | `resolve()` normalizes `..` sequences before comparison |

**Key insight:** The scope of this phase is narrow — two endpoints and one page. Every hard problem (markdown rendering, routing, state management) is already solved by installed libraries. The only new code is wiring.

---

## Common Pitfalls

### Pitfall 1: FastAPI Route Ordering — `/tree` and `/file` Suffixes

**What goes wrong:** FastAPI matches routes in registration order. The existing catch-all `/{path:path}` SPA fallback (line 267 of app.py) could swallow requests to `/api/docs/...` if the new routes are registered after the static file handler.

**Why it happens:** The SPA fallback `/{path:path}` is registered last and only serves `index.html`, so it does not swallow `/api/` prefixed paths in practice — but ordering within `/api/` matters if routes share prefix segments.

**How to avoid:** Register both new `/api/docs/...` routes immediately after the existing `/api/quick-tasks/...` route (line 231 in app.py), before the WebSocket handler and static file mounts.

**Warning signs:** Endpoint returns 200 with HTML content instead of JSON — means the SPA catch-all is responding.

### Pitfall 2: Windows Backslashes in `planningPath`

**What goes wrong:** `activeSegment.planningPath` on Windows is `D:\path\to\.planning`. When this is placed in a URL (even URL-encoded), the server's `unquote()` produces a string with backslashes. `Path(backslash_string)` works correctly on Windows but `path.startswith(root_str)` may fail if one uses forward slashes and the other uses backslashes.

**Why it happens:** Mixed slash conventions when comparing strings vs. using `Path` objects.

**How to avoid:** Always call `.resolve()` on both `root` and `target` before comparing. `Path.resolve()` normalizes slashes. Compare `Path` objects or use `root in target.parents`, never raw string prefix comparison.

**Warning signs:** Path traversal guard raises 403 on legitimate files; or guard passes when it should reject.

### Pitfall 3: `planningPath` for GSD-2 Projects

**What goes wrong:** For GSD-2 projects, `planningPath` points to `.gsd/` not `.planning/`. The doc browser should still work — it just shows the `.gsd/` directory contents instead.

**Why it happens:** `_segment_to_json` in app.py sets `planningPath = seg.planning_path`, which is `str(gsd_dir)` for GSD-2 segments (project_discovery.py line 518).

**How to avoid:** The backend endpoints are agnostic to GSD version — they operate on whatever `planning_path` they receive. No special casing needed. The frontend just passes `activeSegment.planningPath` without filtering by version.

**Warning signs:** Docs page shows empty tree for GSD-2 projects.

### Pitfall 4: Root File Auto-Select (D-10) Race Condition

**What goes wrong:** On initial render, the tree fetch and the auto-select of ROADMAP.md happen simultaneously. If ROADMAP.md fetch fires before the tree returns, the tree highlight won't show the selection.

**Why it happens:** Two independent `useEffect` hooks both depend on `planningPath`.

**How to avoid:** The highlight state is driven by `selectedPath` (local state). The tree renders the highlight purely based on whether `node.path === selectedPath`. Since both the tree fetch and the initial file fetch use the same `planningPath` trigger, the tree and content will both be populated in the same React render cycle after their respective fetches complete. No special coordination needed — just ensure the tree node highlight uses `node.path === selectedPath` comparison with forward-slash-normalized paths.

**Warning signs:** ROADMAP.md content displays but no tree node shows as selected.

### Pitfall 5: D-06 Quick-Access Duplicate Paths

**What goes wrong:** The quick-access shortcuts (D-04) and the full tree both show the same files. Clicking either must set the same `selectedPath` and thus highlight both. If path formats differ (one uses backslashes, one uses forward slashes, or absolute vs. relative), the same file will appear selected in one location but not the other.

**Why it happens:** Quick-access section constructs paths as literals (`"ROADMAP.md"`), while the tree nodes receive paths from the backend (which builds them as relative paths using `/`).

**How to avoid:** Use a single canonical path format throughout — relative to planning root, forward slashes. Backend tree endpoint should always return `path` values with forward slashes (`str(rel).replace("\\", "/")`). Frontend quick-access section uses the same string constants that match this format.

---

## Code Examples

Verified patterns from existing codebase:

### React-markdown import and usage (existing in DashboardPage.tsx)
```tsx
// Source: DashboardPage.tsx lines 2-3
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Usage in JSX (Source: DashboardPage.tsx line 179)
<div className="prose prose-invert prose-sm max-w-none">
  <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
</div>
```

### fetchQuickTasks pattern to follow for fetchDocTree (existing in api.ts)
```ts
// Source: api.ts lines 49-55
export async function fetchQuickTasks(planningPath: string): Promise<QuickTaskPayload[]> {
  const enc = encodeURIComponent(planningPath);
  const r = await fetch(`${base}/api/quick-tasks/${enc}`, noStore);
  if (!r.ok) throw new Error(await r.text());
  const j = await r.json();
  return j.tasks ?? [];
}
```

### Backend quick-tasks handler to follow for docs endpoints (existing in app.py)
```python
# Source: gsd_monitor/api/app.py lines 231-237
@application.get("/api/quick-tasks/{planning_path:path}")
async def quick_tasks(planning_path: str) -> dict[str, Any]:
    from urllib.parse import unquote
    p = unquote(planning_path)
    tasks = QuickTaskParser.parse(p)
    return {"tasks": [t.model_dump(mode="json") for t in tasks]}
```

### NavLink active state pattern (existing in ShellLayout.tsx)
```tsx
// Source: ShellLayout.tsx lines 163-172
<NavLink
  key={item.to}
  to={item.to}
  className={({ isActive }) =>
    `rounded-md px-3 py-2 text-sm font-medium ${isActive ? "bg-[#2a2d2e] text-[#cccccc]" : "text-[#858585] hover:bg-[#2a2d2e] hover:text-[#cccccc]"}`
  }
>
  {item.label}
</NavLink>
```

### Route registration pattern (existing in App.tsx)
```tsx
// Source: App.tsx lines 14-21
<Routes>
  <Route path="/" element={<Navigate to="/dashboard" replace />} />
  <Route path="/dashboard" element={<DashboardPage />} />
  {/* Add here: <Route path="/docs" element={<DocsPage />} /> */}
  <Route path="/drift" element={<DriftPage />} />
  ...
</Routes>
```

---

## Environment Availability

Step 2.6: External dependencies for this phase are all provided by the existing project stack. No new external tools, services, or CLI utilities are required.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Backend endpoints | Yes | 3.13.7 | — |
| Node.js | Frontend build | Yes | 22.16.0 | — |
| npm | Frontend build | Yes | 11.11.1 | — |
| react-markdown | DocsPage rendering | Yes (in package.json) | 10.0 | — |
| remark-gfm | DocsPage GFM support | Yes (in package.json) | 4.0 | — |

All dependencies present. No missing dependencies.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tailwind config file (`tailwind.config.js`) | `@tailwindcss/vite` plugin, arbitrary hex values inline | Tailwind v4 (this project) | No config file needed; use `bg-[#hex]` directly |
| `react-markdown` with `remark-gfm` v3 | `react-markdown` 10 + `remark-gfm` 4 | 2024 | Already installed; API identical for this use case |

---

## Open Questions

1. **Tree depth for large repos**
   - What we know: `.planning/phases/` can have many subdirectories (one per phase, each with multiple files)
   - What's unclear: Whether the recursive tree build will be slow for repos with 20+ phases
   - Recommendation: Build the full tree synchronously on the backend (it's disk I/O on a local path, already in the planning directory the watcher monitors). If needed, a depth limit can be added, but it is not expected to be necessary for v1.

2. **GSD-2 quick-access files**
   - What we know: GSD-2 uses `.gsd/` with `milestones/` structure, not `ROADMAP.md` / `STATE.md` / `REQUIREMENTS.md`
   - What's unclear: Whether the quick-access shortcuts should be different for GSD-2 (e.g., show `roadmap.md` from the `.gsd/` root if it exists instead)
   - Recommendation: Attempt to show the 4 curated shortcuts by checking if each file exists in the planning root. If a file doesn't exist, omit it from quick-access (same logic as D-07 for PLAN.md). This handles GSD-2 gracefully without special-casing.

---

## Sources

### Primary (HIGH confidence)
- `gsd_monitor/api/app.py` — lines 231-237 for quick-tasks route pattern; lines 254-274 for SPA fallback ordering
- `frontend/src/api.ts` — lines 1-55 for fetch pattern, `noStore`, `encodeURIComponent` usage
- `frontend/src/pages/DashboardPage.tsx` — lines 1-3 for react-markdown import; line 179 for rendering pattern
- `frontend/src/ShellLayout.tsx` — lines 6-12 for nav array; lines 163-172 for NavLink pattern
- `frontend/src/App.tsx` — route registration pattern
- `frontend/src/context.tsx` — `useApp()` context shape; `activeSegment.planningPath` availability
- `gsd_monitor/services/project_discovery.py` — lines 344-348 for `artifact_paths` composition (plan files); lines 240-242 for GSD-1 `planning_path`; lines 518-528 for GSD-2 `planning_path`
- `gsd_monitor/models/core.py` — `PhaseEntry.artifact_paths` field definition

### Secondary (MEDIUM confidence)
- Python `pathlib.Path.resolve()` + parent traversal guard — standard Python security pattern, verified by practice in the codebase (path operations throughout project_discovery.py)
- FastAPI `{param:path}` path converter behavior with literal suffixes — confirmed by the existing `/api/quick-tasks/{planning_path:path}` pattern working in production

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already installed, versions confirmed in package.json / pyproject.toml
- Architecture: HIGH — all patterns derived directly from existing production code in the repo
- Pitfalls: HIGH — derived from concrete code inspection (slash normalization, route ordering, path traversal)

**Research date:** 2026-04-04
**Valid until:** 2026-05-04 (stable stack, no fast-moving dependencies)
