import pytest
from fastapi.testclient import TestClient

from gsd_monitor.api import app as app_module
from gsd_monitor.api.app import create_app
from gsd_monitor.services.settings_service import SettingsService


def test_put_settings_json_body_not_query(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression: all-optional Pydantic models need Body(...) or FastAPI treats them as query params."""
    monkeypatch.setenv("GSD_MONITOR_SETTINGS_PATH", str(tmp_path / "cfg.json"))
    app_module.state.settings_service = SettingsService()
    try:
        c = TestClient(create_app())
        r = c.put("/api/settings", json={"scan_roots": [r"D:\test-scan-root"]})
        assert r.status_code == 200, r.text
        assert r.json()["scan_roots"] == [r"D:\test-scan-root"]
        r2 = c.get("/api/settings")
        assert r2.json()["scan_roots"] == [r"D:\test-scan-root"]
    finally:
        app_module.state.settings_service = SettingsService()


def test_browse_folder_returns_json() -> None:
    c = TestClient(create_app())
    r = c.post("/api/browse-folder")
    assert r.status_code == 200
    j = r.json()
    assert "paths" in j and "cancelled" in j


def test_health() -> None:
    c = TestClient(create_app())
    r = c.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_groups() -> None:
    c = TestClient(create_app())
    r = c.get("/api/groups")
    assert r.status_code == 200
    assert "groups" in r.json()
