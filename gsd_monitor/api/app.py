"""FastAPI application — REST + WebSocket + static SPA."""

from __future__ import annotations

import asyncio
import collections
import json
import logging
import sys
import threading
import time
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
from gsd_monitor.parsers.requirements_parser import RequirementsParser
from gsd_monitor.services.project_discovery import ProjectDiscoveryService, ProjectGroup, SegmentModel, WorktreeInfo
from gsd_monitor.services.settings_service import SettingsService


class _InMemoryHandler(logging.Handler):
    """Thread-safe in-memory log handler with a capped ring buffer."""

    def __init__(self, maxlen: int = 2000) -> None:
        super().__init__()
        self._records: collections.deque[dict[str, Any]] = collections.deque(maxlen=maxlen)
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry: dict[str, Any] = {
                "ts": record.created,
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
            }
            with self._lock:
                self._records.append(entry)
        except Exception:
            pass

    def get_all(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._records)

    def clear(self) -> None:
        with self._lock:
            self._records.clear()


# Module-level handler — attached to the gsd_monitor root logger so all
# sub-loggers (discovery, parsers, settings, etc.) flow through it.
_log_handler = _InMemoryHandler()
_log_handler.setFormatter(logging.Formatter("%(message)s"))

_gsd_root = logging.getLogger("gsd_monitor")
_gsd_root.setLevel(logging.DEBUG)
_gsd_root.addHandler(_log_handler)

logger = logging.getLogger(__name__)


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
        self._dirty: bool = False

    def _on_fs_change(self, _root: str) -> None:
        logger.debug("[fs-change] event on root=%s", _root)
        acquired = self._refresh_lock.acquire(blocking=False)
        if not acquired:
            self._dirty = True  # Signal that a change arrived during an active scan
            logger.debug("[fs-change] refresh already running — marked dirty")
            return
        try:
            while True:
                self._dirty = False
                logger.debug("[fs-change] starting re-scan")
                t0 = time.monotonic()
                s = self.settings_service.load()
                self.groups = self.discovery.discover_groups(s.scan_roots)
                elapsed = time.monotonic() - t0
                logger.debug(
                    "[fs-change] scan done in %.3fs — %d group(s)", elapsed, len(self.groups)
                )
                # Do NOT rebuild watchers here — roots only change on settings save,
                # and stop()/restart on every FS event creates brief monitoring gaps.
                if not self._dirty:
                    break
                logger.debug("[fs-change] dirty flag set — re-scanning")
        finally:
            self._refresh_lock.release()
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._broadcast({"type": "projects_updated"}), self._loop)

    def refresh(self) -> None:
        logger.info("[refresh] starting full scan (scan_roots=%s)", self.settings_service.load().scan_roots)
        t0 = time.monotonic()
        with self._refresh_lock:
            while True:
                self._dirty = False
                s = self.settings_service.load()
                logger.debug("[refresh] discover_groups with %d root(s)", len(s.scan_roots))
                self.groups = self.discovery.discover_groups(s.scan_roots)
                elapsed = time.monotonic() - t0
                logger.info(
                    "[refresh] scan complete in %.3fs — %d group(s) found", elapsed, len(self.groups)
                )
                if not self._dirty:
                    break
                logger.debug("[refresh] dirty flag set — re-scanning")
            self.watcher.set_roots(list(s.scan_roots))

    async def connect_ws(self, ws: WebSocket) -> None:
        await ws.accept()
        self._ws.add(ws)
        logger.debug("[ws] client connected — %d active", len(self._ws))

    def disconnect_ws(self, ws: WebSocket) -> None:
        self._ws.discard(ws)
        logger.debug("[ws] client disconnected — %d active", len(self._ws))

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


def _extract_wave_data(planning_dir: str) -> list[dict[str, Any]]:
    """Extract multi-wave phase data from PLAN.md frontmatter.

    Reads all *-PLAN.md files under planning_dir/phases/, extracts the wave:
    field from YAML-like frontmatter (bounded by --- delimiters), and returns
    only phases where plans span more than one distinct wave value.

    Args:
        planning_dir: Path to the .planning/ directory.

    Returns:
        List of dicts, each with phase_number (int), phase_title (str), and
        plans (list of dicts with plan_name and wave). Sorted by phase_number;
        plans within each phase sorted by wave ascending.
    """
    import re as _re

    _WAVE_RE = _re.compile(r"^wave:\s*(\d+)", _re.MULTILINE)
    _PLAN_NUM_RE = _re.compile(r"^plan:\s*(\S+)", _re.MULTILINE)

    phases_dir = Path(planning_dir) / "phases"
    if not phases_dir.is_dir():
        return []

    # Map: phase_dir_name -> list of (plan_name, wave)
    phase_data: dict[str, list[dict[str, Any]]] = {}

    for subdir in sorted(phases_dir.iterdir()):
        if not subdir.is_dir():
            continue
        dir_name = subdir.name
        plan_files = sorted(subdir.glob("*-PLAN.md"))
        if not plan_files:
            continue

        plans_in_phase: list[dict[str, Any]] = []
        for plan_file in plan_files:
            try:
                content = plan_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            # Extract YAML frontmatter between first pair of --- delimiters
            frontmatter = ""
            if content.startswith("---"):
                end_idx = content.find("---", 3)
                if end_idx != -1:
                    frontmatter = content[3:end_idx]

            wave_m = _WAVE_RE.search(frontmatter)
            if wave_m is None:
                continue
            wave = int(wave_m.group(1))

            # Use plan: field from frontmatter for plan name, fall back to filename stem
            plan_num_m = _PLAN_NUM_RE.search(frontmatter)
            plan_name = plan_num_m.group(1).strip() if plan_num_m else plan_file.stem

            plans_in_phase.append({"plan_name": str(plan_name), "wave": wave})

        if plans_in_phase:
            phase_data[dir_name] = plans_in_phase

    # Build result list — only include phases with more than one distinct wave value
    result: list[dict[str, Any]] = []
    for dir_name, plans in phase_data.items():
        distinct_waves = {p["wave"] for p in plans}
        if len(distinct_waves) <= 1:
            continue

        # Extract phase_number and phase_title from directory name
        # Pattern: "11-gsd-core-support" -> number=11, title="gsd-core-support"
        num_m = _re.match(r"^(\d+)-(.+)$", dir_name)
        if num_m:
            phase_number = int(num_m.group(1))
            phase_title = num_m.group(2).replace("-", " ").title()
        else:
            phase_number = 0
            phase_title = dir_name

        # Sort plans by wave ascending
        sorted_plans = sorted(plans, key=lambda p: p["wave"])
        result.append(
            {
                "phase_number": phase_number,
                "phase_title": phase_title,
                "plans": sorted_plans,
            }
        )

    # Sort result by phase_number ascending
    result.sort(key=lambda x: x["phase_number"])
    return result


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup: capture event loop and trigger initial scan. Shutdown: stop file watcher."""
    logger.info("[startup] GSD Monitor API starting up")
    state._loop = asyncio.get_running_loop()
    asyncio.create_task(_run_refresh_background(settings_saved=False))
    yield
    logger.info("[shutdown] GSD Monitor API shutting down")
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

    @application.get("/api/logs")
    async def get_logs() -> dict[str, Any]:
        return {"logs": _log_handler.get_all()}

    @application.delete("/api/logs")
    async def delete_logs() -> dict[str, str]:
        _log_handler.clear()
        logger.info("[logs] log buffer cleared")
        return {"status": "cleared"}

    @application.get("/api/insights/{planning_path:path}")
    async def insights(planning_path: str) -> dict[str, Any]:
        from urllib.parse import unquote

        p = unquote(planning_path)
        requirements = RequirementsParser.parse(p)
        wave_phases = _extract_wave_data(p)
        return {
            "requirements": [r.model_dump() for r in requirements],
            "wave_phases": wave_phases,
        }

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
            stat = target.stat()
        except Exception:
            raise HTTPException(status_code=500, detail="could not read file")
        from datetime import datetime, timezone
        created_at = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        return {"content": content, "created_at": created_at, "modified_at": modified_at}

    @application.post("/api/docs/{planning_path:path}/open")
    async def docs_open_file(planning_path: str, path: str = "") -> dict[str, Any]:
        import os
        from urllib.parse import unquote
        root = Path(unquote(planning_path)).resolve()
        if not root.is_dir():
            raise HTTPException(status_code=404, detail="planning path not found")
        target = (root / path).resolve()
        if root not in target.parents and target != root:
            raise HTTPException(status_code=403, detail="path outside planning directory")
        if not target.is_file():
            raise HTTPException(status_code=404, detail="file not found")
        try:
            os.startfile(str(target))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"could not open file: {exc}")
        return {"ok": True}

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
