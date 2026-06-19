"""Tests for gsd-core discovery features added in phase 11.

Covers: gsd-core detection, HANDOFF.json, config.json surfacing,
.continue-here.md, new doc flags, progress wiring, _try_read_json.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gsd_monitor.models.enums import GsdVersion, PhaseStatus
from gsd_monitor.services.project_discovery import (
    ProjectDiscoveryService,
    _try_read_json,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_project(tmp_path: Path, *, config_json: dict | None = None,
                   roadmap: str = "", state: str = "",
                   handoff: dict | None = None,
                   continue_here: bool = False,
                   phases: dict[str, list[str]] | None = None,
                   requirements: bool = False) -> Path:
    """Create a minimal project layout under tmp_path and return repo root."""
    repo = tmp_path / "repo"
    planning = repo / ".planning"
    planning.mkdir(parents=True)

    if config_json is not None:
        (planning / "config.json").write_text(json.dumps(config_json), encoding="utf-8")

    if roadmap:
        (planning / "ROADMAP.md").write_text(roadmap, encoding="utf-8")

    if state:
        (planning / "STATE.md").write_text(state, encoding="utf-8")

    if handoff is not None:
        (planning / "HANDOFF.json").write_text(json.dumps(handoff), encoding="utf-8")

    if continue_here:
        (planning / ".continue-here.md").write_text("resume here", encoding="utf-8")

    if requirements:
        (planning / "REQUIREMENTS.md").write_text("# Requirements\n", encoding="utf-8")

    if phases:
        phases_dir = planning / "phases"
        phases_dir.mkdir()
        for dir_name, files in phases.items():
            phase_dir = phases_dir / dir_name
            phase_dir.mkdir()
            for fname in files:
                (phase_dir / fname).write_text(f"# {fname}\n", encoding="utf-8")

    # Need a .git dir so canonical root resolution works
    (repo / ".git").mkdir()

    return repo


def _discover_single(tmp_path: Path, **kwargs) -> tuple:
    """Set up a project and discover it. Returns (project, segment)."""
    repo = _setup_project(tmp_path, **kwargs)
    svc = ProjectDiscoveryService(git=None)
    groups = svc.discover_groups([str(tmp_path)])
    assert len(groups) == 1
    seg = groups[0].segments[0]
    return seg.project, seg


# ---------------------------------------------------------------------------
# _try_read_json
# ---------------------------------------------------------------------------

class TestTryReadJson:
    def test_valid_json(self, tmp_path: Path):
        p = tmp_path / "data.json"
        p.write_text('{"key": "value"}', encoding="utf-8")
        assert _try_read_json(p) == {"key": "value"}

    def test_missing_file(self, tmp_path: Path):
        assert _try_read_json(tmp_path / "nope.json") is None

    def test_invalid_json(self, tmp_path: Path):
        p = tmp_path / "bad.json"
        p.write_text("{not valid json", encoding="utf-8")
        assert _try_read_json(p) is None

    def test_non_dict_json(self, tmp_path: Path):
        p = tmp_path / "array.json"
        p.write_text('[1, 2, 3]', encoding="utf-8")
        assert _try_read_json(p) is None

    def test_empty_file(self, tmp_path: Path):
        p = tmp_path / "empty.json"
        p.write_text("", encoding="utf-8")
        assert _try_read_json(p) is None


# ---------------------------------------------------------------------------
# gsd-core detection
# ---------------------------------------------------------------------------

GSD1_ROADMAP = """\
# Roadmap

- [x] **Phase 1: Setup**
- [ ] **Phase 2: Build**
"""

CORE_ROADMAP = """\
# Roadmap: Test Project

## Phase Details

### Phase 1: Setup

**Goal**: Initialize the project

### Phase 2: Build

**Goal**: Build the feature
"""


class TestGsdCoreDetection:
    def test_config_json_triggers_core(self, tmp_path: Path):
        proj, seg = _discover_single(
            tmp_path,
            config_json={"mode": "adaptive"},
            roadmap=CORE_ROADMAP,
        )
        assert proj.version == GsdVersion.CORE
        assert seg.gsd_version == GsdVersion.CORE

    def test_heading_sniff_triggers_core(self, tmp_path: Path):
        proj, seg = _discover_single(
            tmp_path,
            roadmap=CORE_ROADMAP,
        )
        assert proj.version == GsdVersion.CORE

    def test_checkbox_roadmap_stays_gsd1(self, tmp_path: Path):
        proj, seg = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
        )
        assert proj.version == GsdVersion.V1

    def test_config_json_with_checkbox_roadmap_still_core(self, tmp_path: Path):
        """config.json is authoritative even if roadmap uses checkbox format."""
        proj, _ = _discover_single(
            tmp_path,
            config_json={"mode": "adaptive"},
            roadmap=GSD1_ROADMAP,
        )
        assert proj.version == GsdVersion.CORE


# ---------------------------------------------------------------------------
# HANDOFF.json
# ---------------------------------------------------------------------------

class TestHandoffJson:
    def test_handoff_populates_info(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            handoff={"phase": "5", "plan": "02", "timestamp": "2026-06-18T10:00:00Z"},
        )
        assert proj.handoff_info is not None
        assert proj.handoff_info["phase"] == "5"
        assert proj.handoff_info["plan"] == "02"
        assert proj.handoff_info["timestamp"] == "2026-06-18T10:00:00Z"
        assert proj.handoff_info["paused"] is True

    def test_handoff_missing_keys_default(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            handoff={},
        )
        assert proj.handoff_info is not None
        assert proj.handoff_info["phase"] == ""
        assert proj.handoff_info["plan"] == ""
        assert proj.handoff_info["timestamp"] == ""
        assert proj.handoff_info["paused"] is True

    def test_no_handoff_leaves_none(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
        )
        assert proj.handoff_info is None

    def test_malformed_handoff_ignored(self, tmp_path: Path):
        """Invalid JSON in HANDOFF.json should not crash discovery."""
        repo = _setup_project(tmp_path, roadmap=GSD1_ROADMAP)
        (repo / ".planning" / "HANDOFF.json").write_text("{bad json", encoding="utf-8")
        svc = ProjectDiscoveryService(git=None)
        groups = svc.discover_groups([str(tmp_path)])
        assert len(groups) == 1
        proj = groups[0].segments[0].project
        assert proj.handoff_info is None


# ---------------------------------------------------------------------------
# .continue-here.md
# ---------------------------------------------------------------------------

class TestContinueHere:
    def test_continue_here_detected(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            continue_here=True,
        )
        assert proj.continue_here is True

    def test_no_continue_here_defaults_false(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
        )
        assert proj.continue_here is False


# ---------------------------------------------------------------------------
# config.json surfacing
# ---------------------------------------------------------------------------

class TestConfigInfoSurfacing:
    def test_full_config_extracted(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            config_json={
                "mode": "adaptive",
                "model_profile": "opus",
                "git": {"branching_strategy": "phase-branch"},
            },
            roadmap=CORE_ROADMAP,
        )
        assert proj.config_info is not None
        assert proj.config_info["workflow_mode"] == "adaptive"
        assert proj.config_info["model_profile"] == "opus"
        assert proj.config_info["branching_strategy"] == "phase-branch"

    def test_discuss_mode_fallback(self, tmp_path: Path):
        """workflow.discuss_mode used when top-level mode is absent."""
        proj, _ = _discover_single(
            tmp_path,
            config_json={
                "workflow": {"discuss_mode": "collaborative"},
            },
            roadmap=CORE_ROADMAP,
        )
        assert proj.config_info["workflow_mode"] == "collaborative"

    def test_sparse_config(self, tmp_path: Path):
        """Config with no relevant keys still produces config_info with Nones."""
        proj, _ = _discover_single(
            tmp_path,
            config_json={},
            roadmap=CORE_ROADMAP,
        )
        assert proj.config_info is not None
        assert proj.config_info["workflow_mode"] is None
        assert proj.config_info["model_profile"] is None
        assert proj.config_info["branching_strategy"] is None

    def test_no_config_json_leaves_none(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
        )
        assert proj.config_info is None


# ---------------------------------------------------------------------------
# New doc type flags in _enrich_phase
# ---------------------------------------------------------------------------

class TestDocTypeFlags:
    def test_has_ui_spec(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            phases={"01-setup": ["01-UI-SPEC.md"]},
        )
        phase = proj.milestones[0].phases[0]
        assert phase.has_ui_spec is True
        assert phase.has_ui_review is False

    def test_has_ui_review(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            phases={"01-setup": ["01-UI-REVIEW.md"]},
        )
        phase = proj.milestones[0].phases[0]
        assert phase.has_ui_review is True

    def test_has_summary(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            phases={"01-setup": ["01-01-SUMMARY.md"]},
        )
        phase = proj.milestones[0].phases[0]
        assert phase.has_summary is True

    def test_has_requirements(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            requirements=True,
            phases={"01-setup": ["01-01-PLAN.md"]},
        )
        phase = proj.milestones[0].phases[0]
        assert phase.has_requirements is True

    def test_no_doc_flags_default_false(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            phases={"01-setup": ["01-01-PLAN.md"]},
        )
        phase = proj.milestones[0].phases[0]
        assert phase.has_ui_spec is False
        assert phase.has_ui_review is False
        assert phase.has_summary is False
        assert phase.has_requirements is False


# ---------------------------------------------------------------------------
# Progress wiring from StateParser to GsdProject
# ---------------------------------------------------------------------------

class TestProgressWiring:
    def test_yaml_progress_wired_to_project(self, tmp_path: Path):
        state = """\
---
progress:
  total_phases: 12
  completed_phases: 8
  percent: 67
---

# State
"""
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            state=state,
        )
        assert proj.total_phases == 12
        assert proj.completed_phases == 8
        assert proj.progress_percent == 67

    def test_bold_inline_progress_wired(self, tmp_path: Path):
        state = """\
# State

**total_phases:** 5
**completed_phases:** 3
**progress_percent:** 60
"""
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            state=state,
        )
        assert proj.total_phases == 5
        assert proj.completed_phases == 3
        assert proj.progress_percent == 60

    def test_no_progress_defaults_zero(self, tmp_path: Path):
        state = "# State\n\n**Active Milestone:** v1.0\n"
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
            state=state,
        )
        assert proj.total_phases == 0
        assert proj.completed_phases == 0
        assert proj.progress_percent == 0

    def test_no_state_file_defaults_zero(self, tmp_path: Path):
        proj, _ = _discover_single(
            tmp_path,
            roadmap=GSD1_ROADMAP,
        )
        assert proj.total_phases == 0
        assert proj.completed_phases == 0
        assert proj.progress_percent == 0


# ---------------------------------------------------------------------------
# GSD-2 REMOVAL: verify .gsd/ projects are NOT discovered (DETECT-06)
# ---------------------------------------------------------------------------

class TestGsd2Removal:
    def test_gsd2_only_project_not_discovered(self, tmp_path: Path):
        """A directory with only .gsd/ (no .planning/) should NOT be discovered."""
        repo = tmp_path / "gsd2-only-repo"
        repo.mkdir()

        # Create a .gsd directory (GSD-2 marker)
        gsd_dir = repo / ".gsd"
        gsd_dir.mkdir()
        (gsd_dir / "ROADMAP.md").write_text("# GSD-2 Roadmap\n", encoding="utf-8")

        # No .planning directory — this should NOT be discovered
        # Even if there's a .git directory
        (repo / ".git").mkdir()

        svc = ProjectDiscoveryService(git=None)
        groups = svc.discover_groups([str(tmp_path)])

        # Should return empty list (no projects discovered)
        assert len(groups) == 0
