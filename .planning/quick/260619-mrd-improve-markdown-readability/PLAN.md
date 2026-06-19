---
id: 260619-mrd
title: Improve Markdown Readability
status: in_progress
created: 2026-06-19
---

# Quick Task: Improve Markdown Readability

## Task

The reference panel (right pane in DocsPage) needs two improvements:

1. **Resizable panel** — add a drag handle between the sidebar (file tree) and the content pane so the user can resize the split
2. **Better markdown styling** — use colors and tag formatting to make planning docs more readable

## Scope

- `frontend/src/pages/DocsPage.tsx` — add resize handle + drag logic
- `frontend/src/index.css` — add custom prose overrides for markdown readability

## Implementation Plan

### Task 1: Resizable sidebar

- Add `sidebarWidth` state (default 260, min 160, max 480)
- Add a 4px drag handle `<div>` between `<aside>` and `<main>`
- On mousedown: set isDragging ref, capture starting x and width
- On mousemove (document): update sidebarWidth
- On mouseup (document): clear isDragging
- Use `cursor-col-resize` and visual hover indicator on handle
- Cleanup event listeners in useEffect return

### Task 2: Better markdown prose styling

Add to `index.css` — custom `prose-invert` overrides targeting the `.docs-content` wrapper:
- Headings: h1 in accent blue with bottom border, h2/h3 with left color bar
- Inline code: subtle bg, colored text
- Code blocks: dark bg with border
- Blockquotes: left border accent, muted text
- Tables: striped rows, border
- Horizontal rules: colored
- Checkboxes: styled task list items
