"""Debounced watchdog over scan roots — mirrors FileWatcherService."""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Interval in seconds between health checks of Observer threads.
_HEALTH_CHECK_INTERVAL_S = 15.0


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
        self._health_timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def set_roots(self, roots: list[str]) -> None:
        self._cancel_health_timer()
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
        if self._observers:
            self._schedule_health_check()

    def _schedule_health_check(self) -> None:
        t = threading.Timer(_HEALTH_CHECK_INTERVAL_S, self._health_check)
        t.daemon = True
        t.start()
        self._health_timer = t

    def _cancel_health_timer(self) -> None:
        with self._lock:
            if self._health_timer is not None:
                self._health_timer.cancel()
                self._health_timer = None

    def _health_check(self) -> None:
        """Restart any Observer threads that have died unexpectedly."""
        with self._lock:
            revived: list[tuple[Observer, str]] = []
            for obs, root in self._observers:
                if not obs.is_alive():
                    try:
                        obs.stop()
                    except Exception:
                        pass
                    new_obs = Observer()
                    h = _Handler(self._on_change, root)
                    new_obs.schedule(h, root, recursive=True)
                    try:
                        new_obs.start()
                        revived.append((new_obs, root))
                    except Exception:
                        revived.append((obs, root))
                else:
                    revived.append((obs, root))
            self._observers = revived
        # Reschedule the next health check if there are still active observers.
        if self._observers:
            self._schedule_health_check()

    def stop(self) -> None:
        for obs, _ in self._observers:
            obs.stop()
            obs.join(timeout=2.0)
        self._observers.clear()
