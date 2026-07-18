"""Tests for 999.x backlog phase parsing in gsd-core ROADMAP format."""

from __future__ import annotations

import textwrap

import pytest

from gsd_monitor.parsers.gsd_core_roadmap import (
    GsdCoreRoadmapParser,
    _parse_phase_id,
    _HEADING_PHASE,
    _CHECKBOX_PHASE,
)
from gsd_monitor.models.enums import PhaseStatus
from gsd_monitor.models.core import PhaseEntry


class TestParsePhaseId:
    """Tests for _parse_phase_id with dot-separated backlog IDs."""

    def test_plain_integer(self):
        number, code = _parse_phase_id("5")
        assert number == 5
        assert code is None

    def test_milestone_prefixed(self):
        number, code = _parse_phase_id("1-01")
        assert number == 1
        assert code == "1-01"

    def test_backlog_dot_separated(self):
        number, code = _parse_phase_id("999.1")
        assert number == 999
        assert code == "999.1"

    def test_backlog_dot_separated_high(self):
        number, code = _parse_phase_id("999.12")
        assert number == 999
        assert code == "999.12"

    def test_invalid_returns_zero(self):
        number, code = _parse_phase_id("abc")
        assert number == 0
        assert code is None


class TestHeadingPhaseRegex:
    """Tests for _HEADING_PHASE regex matching dot-separated IDs."""

    def test_matches_plain_phase(self):
        text = "### Phase 5: Some Title"
        m = _HEADING_PHASE.search(text)
        assert m is not None
        assert m.group(1) == "5"
        assert m.group(2) == "Some Title"

    def test_matches_milestone_prefixed(self):
        text = "### Phase 1-01: Title"
        m = _HEADING_PHASE.search(text)
        assert m is not None
        assert m.group(1) == "1-01"

    def test_matches_backlog_dot_separated(self):
        text = "### Phase 999.1: Backlog Feature"
        m = _HEADING_PHASE.search(text)
        assert m is not None
        assert m.group(1) == "999.1"
        assert m.group(2) == "Backlog Feature"

    def test_matches_backlog_in_multiline(self):
        text = textwrap.dedent("""\
            ## Phase Details

            ### Phase 16: Active Phase
            **Goal**: Active goal

            ### Phase 999.1: Deferred Item
            **Goal**: Deferred goal
        """)
        matches = list(_HEADING_PHASE.finditer(text))
        ids = [m.group(1) for m in matches]
        assert "16" in ids
        assert "999.1" in ids


class TestCheckboxPhaseRegex:
    """Tests for _CHECKBOX_PHASE regex matching dot-separated IDs."""

    def test_matches_plain_checkbox(self):
        text = "- [ ] **Phase 5: Title**"
        m = _CHECKBOX_PHASE.search(text)
        assert m is not None
        assert m.group(2) == "5"

    def test_matches_backlog_dot_checkbox(self):
        text = "- [ ] **Phase 999.1: Backlog Feature**"
        m = _CHECKBOX_PHASE.search(text)
        assert m is not None
        assert m.group(2) == "999.1"
        assert m.group(3).strip() == "Backlog Feature"


class TestPhaseDirPrefix:
    """Tests for _phase_dir_prefix with backlog phases."""

    def test_backlog_phase_prefix(self):
        from gsd_monitor.services.project_discovery import _phase_dir_prefix

        phase = PhaseEntry(number=999, code="999.1", title="Backlog Item")
        assert _phase_dir_prefix(phase) == "999"

    def test_plain_phase_prefix(self):
        from gsd_monitor.services.project_discovery import _phase_dir_prefix

        phase = PhaseEntry(number=3, title="Plain Phase")
        assert _phase_dir_prefix(phase) == "03"

    def test_milestone_prefixed_prefix(self):
        from gsd_monitor.services.project_discovery import _phase_dir_prefix

        phase = PhaseEntry(number=1, code="1-01", title="Milestone Phase")
        assert _phase_dir_prefix(phase) == "01-01"
