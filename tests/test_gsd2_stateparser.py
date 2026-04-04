"""Unit tests for GSD-2 StateParser wiring in _discover_gsd2."""

from __future__ import annotations

from pathlib import Path

import pytest


def _make_gsd2_tree(tmp_path: Path, state_content: str | None = None) -> tuple[Path, Path]:
    """Create minimal GSD-2 directory structure. Returns (repo_dir, gsd_dir)."""
    repo_dir = tmp_path / "my-project"
    gsd_dir = repo_dir / ".gsd"
    gsd_dir.mkdir(parents=True)
    # Minimal milestone/roadmap so _discover_gsd2 doesn't bail early
    m_dir = gsd_dir / "milestones" / "M1"
    m_dir.mkdir(parents=True)
    (m_dir / "roadmap.md").write_text(
        "# M1 Roadmap\n\n## Slices\n\n- [x] **S1** — First slice\n",
        encoding="utf-8",
    )
    if state_content is not None:
        (gsd_dir / "state.md").write_text(state_content, encoding="utf-8")
    return repo_dir, gsd_dir


def test_gsd2_stateparser_populates_position(tmp_path: Path) -> None:
    state_md = (
        "# GSD State\n\n"
        "**Active Milestone:** M1\n"
        "**Active Slice:** S3\n"
        "**Active Task:** T2\n"
        "**Phase:** plan\n"
    )
    repo_dir, gsd_dir = _make_gsd2_tree(tmp_path, state_content=state_md)
    from gsd_monitor.services.project_discovery import ProjectDiscoveryService

    svc = ProjectDiscoveryService()
    seg = svc._discover_gsd2(repo_dir, gsd_dir)
    assert seg is not None
    assert seg.state_current_position == "S3"


def test_gsd2_stateparser_none_when_no_state(tmp_path: Path) -> None:
    repo_dir, gsd_dir = _make_gsd2_tree(tmp_path, state_content=None)
    from gsd_monitor.services.project_discovery import ProjectDiscoveryService

    svc = ProjectDiscoveryService()
    seg = svc._discover_gsd2(repo_dir, gsd_dir)
    assert seg is not None
    assert seg.state_current_position is None


def test_gsd2_stateparser_prefers_active_slice_over_status(tmp_path: Path) -> None:
    # Edge case: a state.md that has both GSD State format AND some status-like content
    state_md = (
        "# GSD State\n\n"
        "**Active Milestone:** M1\n"
        "**Active Slice:** S5\n"
        "**Phase:** execute\n"
    )
    repo_dir, gsd_dir = _make_gsd2_tree(tmp_path, state_content=state_md)
    from gsd_monitor.services.project_discovery import ProjectDiscoveryService

    svc = ProjectDiscoveryService()
    seg = svc._discover_gsd2(repo_dir, gsd_dir)
    assert seg is not None
    assert seg.state_current_position == "S5"
