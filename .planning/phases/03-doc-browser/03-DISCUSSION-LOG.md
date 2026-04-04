# Phase 3: Doc Browser - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 03-doc-browser
**Areas discussed:** Layout placement, Quick-access shortcuts, File tree behavior, Backend API shape

---

## Layout placement

| Option | Description | Selected |
|--------|-------------|----------|
| New /docs page | Dedicated route, sidebar nav entry, full two-column split layout (tree left, content right) | ✓ |
| Split panel on Dashboard | Doc browser as a right-side panel alongside the existing phase list | |
| Drawer (full-screen overlay) | Extends existing Drawer component to full-width, triggered from dashboard | |

**User's choice:** New /docs page
**Notes:** Full-width dedicated page with tree/content split is the clear preference.

---

## Quick-access shortcuts

### Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Pinned at top of tree | 4 files pinned above a divider, also in tree at actual locations | ✓ |
| Auto-selected on open | No pinned section; ROADMAP.md pre-selected, user browses from there | |
| Horizontal chips above tree | 4 buttons above the tree panel | |

**User's choice:** Pinned at top of tree

### Active PLAN.md identification

| Option | Description | Selected |
|--------|-------------|----------|
| Plan for the in-progress phase | First in_progress phase → its most recent PLAN.md. Omit if no in-progress phase. | ✓ |
| Most recently modified plan file | Newest mtime across all plan files | |
| All plan files for in-progress phase | Multiple shortcuts if phase has multiple plans | |

**User's choice:** Plan for the in-progress phase

---

## File tree behavior

### Files shown

| Option | Description | Selected |
|--------|-------------|----------|
| .md files only | Only markdown files visible in tree | |
| All files | Every file under .planning/ listed | ✓ |
| .md files + named exceptions | .md plus explicit non-.md inclusions | |

**User's choice:** All files

### Default expand/collapse

| Option | Description | Selected |
|--------|-------------|----------|
| Top-level folders collapsed | phases/, codebase/, quick/ start collapsed | ✓ |
| Fully expanded | All folders open on load | |
| Only phases/ expanded | phases/ auto-expands, others collapsed | |

**User's choice:** Top-level folders collapsed

### Non-.md file behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Show raw text in content pane | Display as plain preformatted text | ✓ |
| Nothing / disabled | Listed but clicking does nothing | |

**User's choice:** Show raw text

### Initial selection

| Option | Description | Selected |
|--------|-------------|----------|
| ROADMAP.md auto-selected | ROADMAP.md pre-rendered on page load | ✓ |
| Nothing selected | Empty state until user picks a file | |

**User's choice:** ROADMAP.md auto-selected

---

## Backend API shape

### Endpoint design

| Option | Description | Selected |
|--------|-------------|----------|
| Two endpoints: tree + content | GET /tree → JSON tree; GET /file?path=... → raw content | ✓ |
| Single endpoint returns everything | Tree + all file contents in one call | |
| Serve files as static assets | Backend mounts .planning/ as static directory | |

**User's choice:** Two endpoints

### Rendering location

| Option | Description | Selected |
|--------|-------------|----------|
| Raw markdown, client renders | API returns raw string; react-markdown renders | ✓ |
| Pre-rendered HTML, server side | Python renders to HTML; dangerouslySetInnerHTML on client | |

**User's choice:** Raw markdown, client renders

---

## Claude's Discretion

- Exact file tree panel width
- Tree node expand/collapse icons
- Whether to show file metadata (size, date) in tree
- Loading state style (spinner vs skeleton)
- Truncation of long filenames
- "Quick access" section header styling

## Deferred Ideas

None — discussion stayed within phase scope.
