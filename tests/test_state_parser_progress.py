"""Tests for StateParser progress metric extraction."""

from pathlib import Path

import pytest

from gsd_monitor.parsers.state_parser import StateParser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, text: str, filename: str = "STATE.md") -> Path:
    p = tmp_path / filename
    p.write_text(text, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# YAML frontmatter progress extraction
# ---------------------------------------------------------------------------

FRONTMATTER_STATE = """\
---
gsd_state_version: 1.0
milestone: v3.0
current_phase: 5
status: executing
progress:
  total_phases: 8
  completed_phases: 4
  total_plans: 12
  completed_plans: 7
  percent: 50
---

# Project State
"""


def test_yaml_frontmatter_progress(tmp_path: Path):
    p = _write(tmp_path, FRONTMATTER_STATE)
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.total_phases == 8
    assert si.completed_phases == 4
    assert si.progress_percent == 50


def test_yaml_frontmatter_zero_progress(tmp_path: Path):
    text = """\
---
progress:
  total_phases: 2
  completed_phases: 0
  percent: 0
---

# State
"""
    p = _write(tmp_path, text)
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.total_phases == 2
    assert si.completed_phases == 0
    assert si.progress_percent == 0


# ---------------------------------------------------------------------------
# Bold inline progress extraction
# ---------------------------------------------------------------------------

BOLD_INLINE_STATE = """\
# GSD State

**Active Milestone:** v2.0
**Active Slice:** Feature Build

**total_phases:** 10
**completed_phases:** 6
**progress_percent:** 60
"""


def test_bold_inline_progress(tmp_path: Path):
    p = _write(tmp_path, BOLD_INLINE_STATE)
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.total_phases == 10
    assert si.completed_phases == 6
    assert si.progress_percent == 60


def test_bold_inline_partial_fields(tmp_path: Path):
    """Only total_phases present — others default to 0."""
    text = """\
# GSD State

**total_phases:** 5
"""
    p = _write(tmp_path, text)
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.total_phases == 5
    assert si.completed_phases == 0
    assert si.progress_percent == 0


# ---------------------------------------------------------------------------
# Pipe-table progress extraction
# ---------------------------------------------------------------------------

PIPE_TABLE_STATE = """\
# Project State

## Progress

| Field | Value |
|-------|-------|
| total_phases | 12 |
| completed_phases | 9 |
| progress_percent | 75 |
"""


def test_pipe_table_progress(tmp_path: Path):
    p = _write(tmp_path, PIPE_TABLE_STATE)
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.total_phases == 12
    assert si.completed_phases == 9
    assert si.progress_percent == 75


def test_pipe_table_percent_alias(tmp_path: Path):
    """'percent' and 'progress_percent' both map to progress_percent."""
    text = """\
# Project State

| total_phases | 6 |
| completed_phases | 3 |
| percent | 50 |
"""
    p = _write(tmp_path, text)
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.total_phases == 6
    assert si.completed_phases == 3
    assert si.progress_percent == 50


# ---------------------------------------------------------------------------
# Missing progress fields — defaults to 0
# ---------------------------------------------------------------------------

def test_missing_progress_defaults_to_zero(tmp_path: Path):
    text = """\
# GSD State

**Active Milestone:** v1.0
"""
    p = _write(tmp_path, text)
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.total_phases == 0
    assert si.completed_phases == 0
    assert si.progress_percent == 0


def test_missing_file_returns_error():
    r = StateParser.parse("/nonexistent/STATE.md")
    assert not r.is_success


def test_empty_file_returns_empty_state_info(tmp_path: Path):
    p = _write(tmp_path, "")
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.total_phases == 0
    assert si.completed_phases == 0
    assert si.progress_percent == 0


# ---------------------------------------------------------------------------
# Existing fields still work after extension
# ---------------------------------------------------------------------------

def test_existing_gsd_state_fields_still_work(tmp_path: Path):
    text = """\
# GSD State

**Active Milestone:** v2.0
**Active Slice:** S05
**Active Task:** T3

**total_phases:** 8
**completed_phases:** 5
"""
    p = _write(tmp_path, text)
    r = StateParser.parse(str(p))
    assert r.is_success
    si = r.value
    assert si.active_milestone == "v2.0"
    assert si.active_slice == "S05"
    assert si.active_task == "T3"
    assert si.total_phases == 8
    assert si.completed_phases == 5
