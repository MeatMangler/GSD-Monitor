import json
import os
from pathlib import Path

import pytest

from gsd_monitor.models.core import AppSettings
from gsd_monitor.services.settings_service import SettingsService


def test_settings_roundtrip_via_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "settings.json"
    monkeypatch.setenv("GSD_MONITOR_SETTINGS_PATH", str(cfg))
    svc = SettingsService()
    s = AppSettings(scan_roots=[r"D:\repos", r"E:\more"])
    svc.save(s)
    assert cfg.is_file()
    loaded = json.loads(cfg.read_text(encoding="utf-8"))
    assert loaded["ScanRoots"] == [r"D:\repos", r"E:\more"]
    assert svc.load().scan_roots == [r"D:\repos", r"E:\more"]


def test_settings_load_legacy_pascal_case(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = tmp_path / "settings.json"
    cfg.write_text(
        json.dumps({"ScanRoots": [r"C:\a"], "Theme": "dark"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("GSD_MONITOR_SETTINGS_PATH", str(cfg))
    svc = SettingsService()
    s = svc.load()
    assert s.scan_roots == [r"C:\a"]
    assert s.theme == "dark"
