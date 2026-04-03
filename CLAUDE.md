<!-- GSD:project-start source:PROJECT.md -->
## Project

**GSD Monitor**

GSD Monitor is a Windows desktop companion app (Python + pywebview + React) that discovers GSD projects on disk and gives developers an immediate visual overview of every GSD workflow document. It scans configured directories, classifies GSD-1 (`.planning/`) and GSD-2 (`.gsd/`) projects, and surfaces roadmap phases, planning docs, and project status through a local FastAPI + React UI rendered in Edge WebView2.

**Core Value:** A developer opens GSD Monitor and within seconds understands exactly where every project stands — which phases are done, what's active, and can read any planning doc — with zero duplicate entries and zero confusion about which project they're looking at.

### Constraints

- **Tech stack**: Python 3.11+ / FastAPI / pywebview / React 19 / Tailwind CSS v4 / Vite 6 — no stack changes
- **Platform**: Windows only (Edge WebView2)
- **Settings**: Must remain compatible with `%LOCALAPPDATA%\WinGSDMonitor\settings.json` PascalCase format
- **Read-only**: App never writes to project files
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.11+ — entire backend (`gsd_monitor/`)
- TypeScript 5.9 — entire frontend (`frontend/src/`)
- HTML/CSS — `frontend/index.html`, `frontend/src/index.css` (Tailwind utility classes)
## Runtime
- Python >=3.11 (required; `pyproject.toml` `requires-python`)
- No `.python-version` or `.nvmrc` present; version enforced only in pyproject constraint
- Node.js (version not pinned; no `.nvmrc` present — PRD does not specify a version either)
- Python: no lockfile present — `pyproject.toml` only specifies minimum bounds (`>=`), no pinned versions
- Node: npm — lockfile `frontend/package-lock.json` is present
## Frameworks
- FastAPI >=0.115.0 — HTTP REST API and WebSocket server (`gsd_monitor/api/app.py`)
- Uvicorn[standard] >=0.32.0 — ASGI server; launched on a random loopback port (`gsd_monitor/main_desktop.py`)
- Pydantic >=2.10.0 — data models and validation (`gsd_monitor/models/core.py`)
- pydantic-settings >=2.6.0 — settings configuration support
- pywebview >=5.3 — wraps the uvicorn HTTP server in an Edge WebView2 window (`gsd_monitor/main_desktop.py`)
- React 19.0 — UI framework (`frontend/src/`)
- react-dom 19.0 — DOM renderer
- react-router-dom 7.0 — client-side routing (`BrowserRouter` in `frontend/src/main.tsx`)
- Tailwind CSS 4.0 — utility-first styling (integrated via `@tailwindcss/vite` plugin)
- Vite 6.0 — dev server and bundler (`frontend/vite.config.ts`)
- @vitejs/plugin-react 5.0 — React Fast Refresh + JSX transform
- TypeScript compiled by `tsc -b` before `vite build` (strict mode enabled)
- pytest >=8.0.0 (dev dependency)
- httpx >=0.28.0 — async HTTP client for FastAPI test client (dev dependency)
## Key Dependencies
- pygit2 >=1.14.0 — git history queries via libgit2 (`gsd_monitor/services/git_service.py`)
- watchdog >=6.0.0 — recursive filesystem watching over scan roots (`gsd_monitor/file_watcher.py`)
- react-markdown 10.0 — renders plan/research markdown content in the UI
- remark-gfm 4.0 — GitHub Flavored Markdown plugin for react-markdown
- PyInstaller >=6.0.0 (dev dependency) — packages the app into a single-file Windows `.exe` (`GSDMonitor.spec`)
## Configuration
- `frontend/tsconfig.json` — target ES2022, strict mode on, path alias `@/*` → `src/*`
- `moduleResolution: bundler` (Vite-compatible)
- `frontend/vite.config.ts` — dev proxy: `/api` → `http://127.0.0.1:8765`, `/ws` → `ws://127.0.0.1:8765`
- `pyproject.toml` — hatchling build backend; wheel packages `gsd_monitor/` only
- `GSDMonitor.spec` — PyInstaller spec; bundles `frontend/dist` as data
- `GSD_MONITOR_SETTINGS_PATH` — optional override for settings file path (`gsd_monitor/services/settings_service.py`)
- `LOCALAPPDATA` — used to resolve default settings path on Windows
## Platform Requirements
- Windows (settings path uses `%LOCALAPPDATA%`, WebView2 uses Edge)
- Node.js + npm for frontend build
- Python 3.11+ with pip/hatch for backend
- Windows only — pywebview targets Edge WebView2 (Windows Chromium-based renderer)
- Distributed as a single PyInstaller `.exe` (no installer; no UX for macOS/Linux)
## PRD Alignment Notes
- All PRD-specified packages are present: FastAPI, uvicorn, pywebview, pygit2, watchdog
- React version is 19 (PRD says React 19) — aligned
- Tailwind version is 4.0 (PRD says Tailwind) — aligned, but v4 is a major rewrite vs v3 (uses `@tailwindcss/vite` plugin, no `tailwind.config.js`)
- Vite version is 6.0; TypeScript is 5.9 — both newer than typical PRD baselines
- **No pinned dependency versions** — `pyproject.toml` uses only `>=` bounds; risk of upstream breakage
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- `snake_case.py` for all modules: `plan_parser.py`, `git_service.py`, `settings_service.py`
- `__init__.py` used only for namespace declaration (one-liners or empty)
- `PascalCase` for all classes: `RoadmapParser`, `SettingsService`, `ProjectDiscoveryService`, `ScanWatcher`
- Service classes named `{Domain}Service`
- Parser classes named `{Domain}Parser`
- `snake_case` for all functions and methods: `discover_groups`, `get_latest_commit_date`, `_try_extract_gsd_phases`
- Private helpers prefixed with `_`: `_static_dir`, `_group_to_json`, `_pick_folders_pywebview`
- Static method helpers on parser classes: `RoadmapParser.parse(file_path)`, `PlanParser.parse(file_path)`
- `snake_case` throughout
- Single-letter loop variables used sparingly: `r` for results, `p` for Path/phase, `m` for match/milestone
- Regex constants in `SCREAMING_SNAKE_CASE` at module level: `_GSD_PHASE`, `_SECTION_SPLIT`, `_SLICE`
- `PascalCase.tsx` for React component files: `App.tsx`, `ShellLayout.tsx`, `DashboardPage.tsx`
- `camelCase.ts` for non-component modules: `api.ts`, `context.tsx`
- Pages in `src/pages/` named `{Feature}Page.tsx`
- React components: `PascalCase` named exports — `export function DashboardPage()`
- Hooks: `camelCase` prefixed with `use` — `useApp()`
- Interfaces: `PascalCase` with descriptive suffix — `GroupPayload`, `SegmentPayload`, `PhasePayload`
- Local variables and props: `camelCase`
## Type Hints
- All function signatures annotated with return types: `def parse(file_path: str) -> ParseResult:`
- `from __future__ import annotations` at the top of every module to enable forward references
- Union types use Python 3.10+ `X | Y` syntax: `str | None`, `list[str] | None`
- Generic collections use lowercase: `list[str]`, `dict[int, str]`, `tuple[Path, str] | None`
- `Any` from `typing` used only where truly untyped (Pydantic `value: Any` in `ParseResult`)
- `tsconfig.json` enables `"strict": true`, `"noUnusedLocals": true`, `"noUnusedParameters": true`
- All interfaces fully typed in `src/api.ts` — no `any` in interface definitions
- Event handlers typed inline: `(e: React.ChangeEvent<HTMLSelectElement>)` patterns
- `type` keyword used for imports of pure types: `import type { GroupPayload }`
## Docstrings
## Error Handling
## Pydantic Models
- `BaseModel` from Pydantic v2 throughout
- `Field(default_factory=list)` for all list fields
- `ConfigDict(populate_by_name=True)` on models that accept both snake_case and PascalCase alias keys
- `AppSettings` uses explicit `alias=` and `validation_alias=` to support legacy PascalCase JSON keys
- `model_dump_json(by_alias=True)` used for writing — produces PascalCase JSON on disk
- `model_validate(data)` used for reading — accepts PascalCase via alias
- `model_copy(update={...})` used for immutable updates instead of mutation
## Import Organization
## React Patterns
- Named exports only (no default exports for pages/components — `App.tsx` is the one exception)
- Function components exclusively — no class components
- Single responsibility: layout (`ShellLayout`), data (`context.tsx`), API calls (`api.ts`) are separate concerns
- Single `AppProvider` / `AppCtx` context in `src/context.tsx` provides all shared state
- `useApp()` custom hook throws if used outside provider
- Local state via `useState` in page components for UI-only concerns (loading flags, form values)
- `useMemo` for derived values from context data (stats, group/workstream lists)
- `useCallback` on `reload` to stabilize identity across renders
- `void` prefix on fire-and-forget async calls: `void reload()`, `void save()`
- `async/await` throughout — no `.then()` chaining except in `useEffect` where `void fetch().then(...)`
- Utility classes inline — no CSS modules or styled components
- Dark theme via `bg-zinc-950`, `text-zinc-100/400/500` color scale
- No custom CSS classes defined beyond `src/index.css` (base reset only)
## Linting and Formatting Config
## Module Design
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## High-Level Component Diagram
```
```
## Pattern Overview
- FastAPI runs in a background daemon thread (not the main thread); pywebview owns the main thread
- Single module-level `RuntimeState` instance acts as application state container (not dependency-injected)
- All discovery is synchronous file I/O, offloaded to thread executor for API calls
- WebSocket clients receive push notifications when file system changes or settings are saved
## Layers
- Purpose: Bootstrap uvicorn server, wait for it to be ready, launch pywebview window
- Location: `gsd_monitor/main_desktop.py`, `gsd_monitor/__main__.py`
- Contains: `main()` function, port selection via ephemeral socket bind
- Depends on: FastAPI `create_app()`, `uvicorn`, `webview`
- Used by: PyInstaller EXE entry point, `python -m gsd_monitor`
- Purpose: Serve REST endpoints, WebSocket events, and static SPA assets
- Location: `gsd_monitor/api/app.py`
- Contains: `create_app()` factory, `RuntimeState` class, all route handlers, `SettingsBody` Pydantic model
- Depends on: All services, parsers, models
- Used by: Frontend SPA via fetch/WebSocket
- Purpose: Domain logic for settings persistence, project discovery, and file watching
- Location: `gsd_monitor/services/`
- Contains: `SettingsService`, `ProjectDiscoveryService`, `PlanningContext`, `iter_planning_contexts`, `GitService`
- Depends on: Parsers, models
- Used by: `RuntimeState` in `api/app.py`
- Purpose: Read-only extraction of structured data from GSD markdown files
- Location: `gsd_monitor/parsers/`
- Contains: `RoadmapParser`, `Gsd2RoadmapParser`, `PlanParser`, `StateParser`, `QuickTaskParser`
- Depends on: `models/core.py`, `models/enums.py`
- Used by: `ProjectDiscoveryService`
- Purpose: Shared Pydantic models and enums
- Location: `gsd_monitor/models/`
- Contains: `AppSettings`, `GsdProject`, `Milestone`, `PhaseEntry`, `TodoItem`, `StateInfo`, `ParseResult`; enums `PhaseStatus`, `DriftIndicator`, `GsdVersion`, `MilestoneStatus`, etc.
- Depends on: Nothing internal
- Used by: All layers
- Purpose: React UI served as compiled static files; communicates with API only via fetch/WebSocket
- Location: `frontend/src/`
- Contains: Pages, context/state, API client module, shell layout
- Depends on: FastAPI endpoints (at runtime via HTTP, no shared types)
- Used by: pywebview WebView2
## Data Flow
## State Management
- `RuntimeState` is a module-level singleton instantiated once at import of `api/app.py`
- `groups` is the only in-memory cache — rebuilt on every `refresh()` call
- Settings are always read from disk on `refresh()`; no in-memory settings cache
- WebSocket connections tracked in `_ws: set[WebSocket]`; dead connections pruned on send failure
- `_refresh_lock: threading.Lock` prevents concurrent refreshes (both from FS watcher and API calls)
- `_loop` captured during FastAPI startup (`asyncio.get_running_loop()`) to allow thread-safe coroutine dispatch
- `AppProvider` (`context.tsx`) is the single React context holding all global state
- `groups: GroupPayload[]` — array of all discovered groups from API
- `selectedGroupId`, `selectedSegmentKey` — user navigation selection (plain `useState`)
- `activeSegment`, `activeProject` — derived via `useMemo` from groups + selection
- No client-side caching beyond React state; every reload re-fetches from API
- WebSocket in `AppProvider` `useEffect` — any `onmessage` triggers `reload()`
## Concurrency Model
```
```
- `_refresh_lock` (threading.Lock): held during `state.refresh()` to prevent re-entrant discovery
- `asyncio.run_coroutine_threadsafe()`: used by watchdog callbacks to dispatch `_broadcast()` back to the event loop
- `loop.run_in_executor(None, state.refresh)`: offloads blocking disk I/O from the async event loop
- Phase enrichment for >4 phases uses `ThreadPoolExecutor(max_workers=min(8, n))` within discovery
## Key Design Patterns
## Deviations from PRD Architecture
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
