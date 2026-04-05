"""Persist settings next to legacy WinGSDMonitor path for optional migration."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from gsd_monitor.models.core import AppSettings

logger = logging.getLogger(__name__)


class SettingsService:
    def __init__(self) -> None:
        override = (os.environ.get("GSD_MONITOR_SETTINGS_PATH") or "").strip()
        if override:
            self._path = Path(override)
        else:
            local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
            self._path = Path(local) / "WinGSDMonitor" / "settings.json"

    def load(self) -> AppSettings:
        try:
            if not self._path.is_file():
                return AppSettings()
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return AppSettings.model_validate(data)
        except Exception as ex:
            logger.warning("Failed to load settings from %s, using defaults: %s", self._path, ex)
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            settings.model_dump_json(indent=2, by_alias=True),
            encoding="utf-8",
        )
