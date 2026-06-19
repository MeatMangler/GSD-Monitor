"""Debounced watchdog over scan roots — mirrors FileWatcherService."""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class _Handler(FileSystemEventHandler):
    def __init__(self, cb: Callable[[str], None], root: str) -> None:
        self._cb = cb
        self._root = root
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._debounce_s = 0.3

    def _fire(self) -> None:
        self._cb(self._root)

    def on_any_event(self, event) -> None:  # noqa: ANN001
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce_s, self._fire)
            self._timer.daemon = True
            self._timer.start()


class ScanWatcher:
    def __init__(self, on_change: Callable[[str], None]) -> None:
        self._on_change = on_change
        self._observers: list[tuple[Observer, str]] = []

    def set_roots(self, roots: list[str]) -> None:
        self.stop()
        for r in roots:
            p = Path(r)
            if not p.is_dir():
                continue
            obs = Observer()
            h = _Handler(self._on_change, str(p.resolve()))
            obs.schedule(h, str(p.resolve()), recursive=True)
            obs.start()
            self._observers.append((obs, str(p.resolve())))

    def stop(self) -> None:
        for obs, _ in self._observers:
            obs.stop()
            obs.join(timeout=2.0)
        self._observers.clear()
