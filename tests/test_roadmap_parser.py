"""Parity smoke tests for roadmap parsing."""

from pathlib import Path

import pytest

from gsd_monitor.parsers.roadmap import RoadmapParser


def test_parse_missing_file():
    r = RoadmapParser.parse("/nonexistent/ROADMAP.md")
    assert not r.is_success


def test_parse_checkbox_phases(tmp_path: Path):
    p = tmp_path / "ROADMAP.md"
    p.write_text(
        """# My Project

- [x] **Phase 1: A** - x
- [ ] **Phase 2: B** - y

### Phase 1:

**Goal**: g1

### Phase 2:

**Goal**: g2
""",
        encoding="utf-8",
    )
    r = RoadmapParser.parse(str(p))
    assert r.is_success
    assert r.value
    assert r.value.name == "My Project"
    ms = r.value.milestones
    assert len(ms) == 1
    phases = ms[0].phases
    assert len(phases) == 2
    assert phases[0].status.value == "complete"
    assert phases[1].status.value == "in_progress"
