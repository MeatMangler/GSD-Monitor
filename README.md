# GSD Monitor

A Windows desktop companion app for GSD workflow projects. GSD Monitor scans your configured directories, discovers GSD projects on disk, and gives you an instant visual overview of every planning document, roadmap phase, and project status — all in a native Edge WebView2 window.

**Open the app. Know exactly where every project stands.**

## About GSD

GSD Monitor was built by and for users of the GSD developer workflow system — a lightweight, spec-driven development methodology for Claude Code.

- **[get-shit-done](https://github.com/gsd-build/get-shit-done)** — the original GSD system by [TÂCHES](https://github.com/gsd-build). A light-weight and powerful meta-prompting, context engineering and spec-driven development system for Claude Code. GSD Monitor was created to serve this workflow and pays tribute to its design.
- **[gsd-core](https://github.com/open-gsd/gsd-core)** — the current evolution of GSD, maintained by [open-gsd](https://github.com/open-gsd). GSD Monitor's active development is built around this project and its updated ROADMAP format.

## Features

- Discovers GSD projects across multiple scan roots — supports both GSD-1 (checkbox-style ROADMAP) and gsd-core (heading-based ROADMAP) formats
- All projects use a `.planning/` directory; format is auto-detected from ROADMAP structure
- Displays roadmap phases with status (done, active, planned, drifted)
- Renders any planning document (PLAN.md, RESEARCH.md, SPEC.md, etc.) in-app with full Markdown support
- Git-aware: shows last commit date and drift indicators per project
- Real-time updates via filesystem watcher — no manual refresh needed
- Zero duplicate entries: git worktrees are resolved back to their canonical project
- Supports flat, workstream, and multi-project `.planning/` layouts
- Read-only: never modifies any project file

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop shell | Python 3.11+ / [pywebview](https://pywebview.flowrl.com/) / Edge WebView2 |
| API server | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Data models | [Pydantic v2](https://docs.pydantic.dev/) |
| Git queries | [pygit2](https://www.pygit2.org/) |
| Filesystem watch | [watchdog](https://python-watchdog.readthedocs.io/) |
| Frontend | React 19 / TypeScript 5.9 / [Tailwind CSS v4](https://tailwindcss.com/) |
| Bundler | [Vite 6](https://vitejs.dev/) |
| Distribution | [PyInstaller](https://pyinstaller.org/) single-file `.exe` |

## Requirements

- Windows 10/11 (Edge WebView2 is required — installed by default on Windows 10 1803+)
- Python 3.11+
- Node.js + npm (for frontend development only)

## Getting Started

### Run from source

```bat
:: 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

:: 2. Install Python dependencies
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings pywebview pygit2 watchdog

:: 3. Build the frontend
cd frontend
npm install
npm run build
cd ..

:: 4. Launch
python -m gsd_monitor
```

Or use the provided launcher:

```bat
start.bat
```

### Development mode

Run the frontend dev server with hot reload alongside the Python backend:

```bat
:: Terminal 1 — Python backend
python -m gsd_monitor

:: Terminal 2 — Vite dev server (proxies /api and /ws to the backend)
cd frontend
npm run dev
```

The Vite dev server proxies `/api` and `/ws` to `http://127.0.0.1:8765` by default.

## Project Format Support

GSD Monitor detects and renders both `.planning/` layout variants:

| Format | Origin | ROADMAP style | Detection |
|---|---|---|---|
| **GSD-1** | [get-shit-done](https://github.com/gsd-build/get-shit-done) | Checkbox task lists (`- [ ]`, `- [x]`) | Checkbox lines in ROADMAP.md |
| **gsd-core** | [gsd-core](https://github.com/open-gsd/gsd-core) | Heading-based phases (`## Phase N: Title`) | `## Phase N` headings in ROADMAP.md |

Both variants support flat, workstream (`workstreams/`), and multi-project sub-directory layouts within `.planning/`.

## Configuration

Settings are stored at `%LOCALAPPDATA%\WinGSDMonitor\settings.json` and managed through the in-app Settings page. The schema uses PascalCase keys:

```json
{
  "ScanRoots": ["C:\\Users\\you\\projects"],
  "Theme": "dark",
  "ClaudeCliPath": "claude",
  "TerminalPath": "wt"
}
```

Override the settings file path via the `GSD_MONITOR_SETTINGS_PATH` environment variable.

## Project Structure

```
gsd_monitor/               # Python backend
  api/app.py               # FastAPI app, REST endpoints, WebSocket
  main_desktop.py          # Entry point: uvicorn + pywebview bootstrap
  models/                  # Pydantic data models and enums
  parsers/
    roadmap.py             # GSD-1 checkbox ROADMAP parser
    gsd_core_roadmap.py    # gsd-core heading-based ROADMAP parser
    plan_parser.py         # PLAN.md parser
    state_parser.py        # STATE.md parser
    quick_task.py          # Quick task parser
    requirements_parser.py # Requirements parser
  services/
    project_discovery.py   # Scan roots → project groups
    planning_layout.py     # .planning/ layout enumeration
    settings_service.py    # Settings persistence
    git_service.py         # pygit2 git history queries
  file_watcher.py          # watchdog filesystem watcher

frontend/                  # React + TypeScript SPA
  src/
    pages/                 # DashboardPage, DocsPage, SettingsPage, ...
    context.tsx            # AppProvider — global state via React context
    api.ts                 # Typed API client
    ShellLayout.tsx        # Navigation shell

assets/                    # App icon
tests/                     # pytest test suite
```

## Running Tests

```bat
pip install pytest httpx
pytest tests/
```

## Building a Distributable

```bat
:: Build the frontend first
cd frontend && npm run build && cd ..

:: Package with PyInstaller (requires GSDMonitor.spec)
pyinstaller GSDMonitor.spec
```

The output `dist/GSDMonitor.exe` is a self-contained single-file executable.

## Platform

Windows only. The app depends on Edge WebView2 (bundled with Windows) and pywebview's Windows backend. No macOS or Linux support is planned.

## License

MIT
