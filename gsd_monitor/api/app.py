"""FastAPI application — REST + WebSocket + static SPA."""

from __future__ import annotations

import asyncio
import json
import sys
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.requests import Request

from gsd_monitor.file_watcher import ScanWatcher
from gsd_monitor.models.core import AppSettings
from gsd_monitor.parsers.quick_task import QuickTaskParser
from gsd_monitor.services.project_discovery import ProjectDiscoveryService, ProjectGroup, SegmentModel, WorktreeInfo
from gsd_monitor.services.settings_service import SettingsService


class SettingsBody(BaseModel):
    """PATCH body: snake_case or PascalCase (legacy). All fields optional."""

    model_config = ConfigDict(populate_by_name=True)

    scan_roots: list[str] | None = Field(default=None, alias="ScanRoots")
    theme: str | None = Field(default=None, alias="Theme")
    claude_cli_path: str | None = Field(default=None, alias="ClaudeCliPath")
    terminal_path: str | None = Field(default=None, alias="TerminalPath")
    notify_on_drift: bool | None = Field(default=None, alias="NotifyOnDrift")
    notify_on_phase_completion: bool | None = Field(
        default=None, alias="NotifyOnPhaseCompletion"
    )
    notify_on_verification_failure: bool | None = Field(
        default=None, alias="NotifyOnVerificationFailure"
    )


def _static_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "frontend" / "dist"
    return Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


class RuntimeState:
    def __init__(self) -> None:
        self.settings_service = SettingsService()
        self.discovery = ProjectDiscoveryService()
        self.watcher = ScanWatcher(self._on_fs_change)
        self.groups: list[ProjectGroup] = []
        self._ws: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._refresh_lock = threading.Lock()

    def _on_fs_change(self, _root: str) -> None:
        acquired = self._refresh_lock.acquire(blocking=False)
        if not acquired:
            return  # Drop event — scan already in progress (PERF-01)
        try:
            s = self.settings_service.load()
            self.groups = self.discovery.discover_groups(s.scan_roots)
            self.watcher.set_roots(list(s.scan_roots))
        finally:
            self._refresh_lock.release()
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._broadcast({"type": "projects_updated"}), self._loop)

    def refresh(self) -> None:
        with self._refresh_lock:
            s = self.settings_service.load()
            self.groups = self.discovery.discover_groups(s.scan_roots)
            self.watcher.set_roots(list(s.scan_roots))

    async def connect_ws(self, ws: WebSocket) -> None:
        await ws.accept()
        self._ws.add(ws)

    def disconnect_ws(self, ws: WebSocket) -> None:
        self._ws.discard(ws)

    async def _broadcast(self, payload: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for ws in self._ws:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._ws.discard(ws)


state = RuntimeState()


async def _run_refresh_background(*, settings_saved: bool) -> None:
    """Disk scan + watchers can take a long time; run off the event loop thread."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, state.refresh)
    if not state._loop:
        return
    if settings_saved:
        await state._broadcast({"type": "settings_saved"})
    await state._broadcast({"type": "projects_updated"})


def _segment_to_json(seg: SegmentModel) -> dict[str, Any]:
    from pathlib import Path

    repo = Path(seg.repo_root)
    quick_root = str(repo / ".planning")
    return {
        "segmentKey": seg.segment_key,
        "gsdProject": seg.gsd_project,
        "workstream": seg.workstream,
        "gsdVersion": seg.gsd_version.value,
        "planningPath": seg.planning_path,
        "repoRoot": seg.repo_root,
        "quickPlanningRoot": quick_root,
        "groupId": seg.group_id,
        "project": json.loads(seg.project.model_dump_json()),
        "stateCurrentPosition": seg.state_current_position,
    }


def _pick_folders_pywebview() -> list[str] | None:
    """Return selected folders, or None if cancelled / dialog unavailable."""
    try:
        import webview
    except ImportError:
        return None
    try:
        w = webview.active_window()
        if w is None and webview.windows:
            w = webview.windows[0]
        if w is None:
            return None
        result = w.create_file_dialog(
            webview.FileDialog.FOLDER,
            allow_multiple=True,
        )
    except Exception:
        return None
    if not result:
        return None
    return [str(p) for p in result]


def _group_to_json(g: ProjectGroup) -> dict[str, Any]:
    return {
        "id": g.id,
        "rootPath": g.root_path,
        "displayName": g.display_name,
        "isWorkspace": g.is_workspace,
        "defaultSegmentKey": g.default_segment_key,
        "activeWorkstreamHint": g.active_workstream_hint,
        "segments": [_segment_to_json(s) for s in g.segments],
        "worktrees": [
            {
                "path": wt.path,
                "branch": wt.branch,
                "isPrimary": wt.is_primary,
            }
            for wt in g.worktrees
        ],
    }


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup: capture event loop and trigger initial scan. Shutdown: stop file watcher."""
    state._loop = asyncio.get_running_loop()
    asyncio.create_task(_run_refresh_background(settings_saved=False))
    yield
    state.watcher.stop()


def create_app() -> FastAPI:
    application = FastAPI(title="GSD Monitor API", lifespan=lifespan)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def no_store_api_responses(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        return response

    @application.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/api/groups")
    async def get_groups() -> dict[str, Any]:
        return {"groups": [_group_to_json(g) for g in state.groups]}

    @application.post("/api/groups/refresh")
    async def post_refresh() -> dict[str, Any]:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, state.refresh)
        return {"groups": [_group_to_json(g) for g in state.groups]}

    @application.get("/api/settings")
    async def get_settings() -> dict[str, Any]:
        s = state.settings_service.load()
        return json.loads(s.model_dump_json())

    @application.put("/api/settings")
    async def put_settings(payload: SettingsBody = Body(...)) -> dict[str, Any]:
        cur = state.settings_service.load()
        data = cur.model_dump()
        for k, v in payload.model_dump(exclude_none=True).items():
            data[k] = v
        new = AppSettings.model_validate(data)
        state.settings_service.save(new)
        out = json.loads(new.model_dump_json())
        asyncio.create_task(_run_refresh_background(settings_saved=True))
        return out

    @application.post("/api/browse-folder")
    async def browse_folder() -> dict[str, Any]:
        loop = asyncio.get_running_loop()
        paths = await loop.run_in_executor(None, _pick_folders_pywebview)
        if paths is None:
            return {"paths": [], "cancelled": True}
        return {"paths": paths, "cancelled": False}

    @application.get("/api/quick-tasks/{planning_path:path}")
    async def quick_tasks(planning_path: str) -> dict[str, Any]:
        from urllib.parse import unquote

        p = unquote(planning_path)
        tasks = QuickTaskParser.parse(p)
        return {"tasks": [t.model_dump(mode="json") for t in tasks]}

    @application.get("/api/docs/{planning_path:path}/tree")
    async def docs_tree(planning_path: str) -> dict[str, Any]:
        from urllib.parse import unquote
        root = Path(unquote(planning_path)).resolve()
        if not root.is_dir():
            raise HTTPException(status_code=404, detail="planning path not found")

        def _build_tree(directory: Path) -> list[dict[str, Any]]:
            nodes: list[dict[str, Any]] = []
            try:
                entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            except PermissionError:
                return nodes
            for entry in entries:
                rel = str(entry.relative_to(root)).replace("\\", "/")
                if entry.is_dir():
                    nodes.append({"name": entry.name, "path": rel, "type": "dir", "children": _build_tree(entry)})
                else:
                    nodes.append({"name": entry.name, "path": rel, "type": "file", "children": []})
            return nodes

        return {"tree": _build_tree(root)}

    @application.get("/api/docs/{planning_path:path}/file")
    async def docs_file(planning_path: str, path: str = "") -> dict[str, Any]:
        from urllib.parse import unquote
        root = Path(unquote(planning_path)).resolve()
        if not root.is_dir():
            raise HTTPException(status_code=404, detail="planning path not found")
        target = (root / path).resolve()
        # Path traversal guard
        if root not in target.parents and target != root:
            raise HTTPException(status_code=403, detail="path outside planning directory")
        if not target.is_file():
            raise HTTPException(status_code=404, detail="file not found")
        try:
            content = target.read_text(encoding="utf-8", errors="replace")
        except Exception:
            raise HTTPException(status_code=500, detail="could not read file")
        return {"content": content}

    @application.websocket("/ws/events")
    async def ws_events(ws: WebSocket) -> None:
        await state.connect_ws(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            state.disconnect_ws(ws)

    static = _static_dir()
    if static.is_dir() and (static / "assets").is_dir():
        application.mount(
            "/assets", StaticFiles(directory=static / "assets"), name="assets"
        )

    @application.get("/")
    async def index_page() -> FileResponse:
        idx = _static_dir() / "index.html"
        if idx.is_file():
            return FileResponse(idx)
        from fastapi.responses import JSONResponse

        return JSONResponse(
            {"detail": "Frontend not built. Run: npm ci --prefix frontend && npm run build --prefix frontend"},
            status_code=503,
        )

    @application.get("/{path:path}")
    async def spa(path: str) -> FileResponse:
        idx = _static_dir() / "index.html"
        if idx.is_file():
            return FileResponse(idx)
        from fastapi.responses import JSONResponse

        return JSONResponse({"detail": "frontend missing"}, status_code=503)

    return application
