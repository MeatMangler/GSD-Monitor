---
id: 260619-mrd
title: Improve Markdown Readability
status: complete
completed: 2026-06-19
---

# Summary

## What was done

Two improvements to the Docs page reference panel:

### 1. Resizable sidebar
- Added `sidebarWidth` state (default 260px, min 160px, max 480px)
- Added a 4px drag handle `<div>` between the file tree sidebar and the markdown content panel
- Document-level `mousemove`/`mouseup` listeners handle the drag; `isDragging` ref avoids stale closure issues
- Handle shows `cursor-col-resize` and highlights blue on hover

### 2. Markdown readability
- Added `.docs-content` CSS class to the ReactMarkdown wrapper in DocsPage
- Added custom prose overrides in `index.css` targeting `.docs-content`:
  - **h1**: VS Code blue (`#569cd6`) with bottom border
  - **h2**: accent green (`#4ec994`) with left color bar
  - **h3**: warm orange (`#ce9178`) with muted left bar
  - **Inline code**: orange text on dark bg with border
  - **Code blocks**: darker bg with border
  - **Blockquotes**: blue left border, muted bg
  - **Tables**: bordered with striped even rows
  - **Task list checkboxes**: accent-colored via `accent-color`
  - **Links**: blue, no underline (underline on hover)
  - **Strong**: brighter white

## Files changed
- `frontend/src/pages/DocsPage.tsx` — resize state/handlers, drag handle, `docs-content` class
- `frontend/src/index.css` — `.docs-content` prose overrides

## Build
- `npm run build` passes cleanly (TypeScript strict + Vite)
