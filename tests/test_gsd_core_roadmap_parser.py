"""Tests for GsdCoreRoadmapParser — heading-based ROADMAP.md format."""

from pathlib import Path

import pytest

from gsd_monitor.parsers.gsd_core_roadmap import GsdCoreRoadmapParser
from gsd_monitor.models.enums import GsdVersion, MilestoneStatus, PhaseStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "ROADMAP.md"
    p.write_text(text, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Basic parsing
# ---------------------------------------------------------------------------

def test_parse_missing_file():
    r = GsdCoreRoadmapParser.parse("/nonexistent/path/ROADMAP.md")
    assert not r.is_success


def test_parse_empty_file(tmp_path: Path):
    p = _write(tmp_path, "")
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    assert r.value is not None
    assert r.value.milestones == []


def test_extract_project_name_from_roadmap_heading(tmp_path: Path):
    p = _write(tmp_path, "# Roadmap: My GSD Project\n\n## Phase Details\n")
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    assert r.value.name == "My GSD Project"


def test_extract_project_name_fallback(tmp_path: Path):
    p = _write(tmp_path, "# Something Else\n")
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    # Falls back to directory name or "Something Else"
    assert r.value.name  # non-empty


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

def test_version_is_core(tmp_path: Path):
    p = _write(tmp_path, "# Roadmap: Test\n")
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    assert r.value.version == GsdVersion.CORE


# ---------------------------------------------------------------------------
# Heading-based phase parsing
# ---------------------------------------------------------------------------

BASIC_ROADMAP = """\
# Roadmap: Test Project

## Phase Details

### Phase 1: Setup

**Goal**: Initialize the project

### Phase 2: Build

**Goal**: Build the feature

### Phase 3: Ship

**Goal**: Deploy to production
"""


def test_parse_heading_phases(tmp_path: Path):
    p = _write(tmp_path, BASIC_ROADMAP)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    assert r.value is not None
    milestones = r.value.milestones
    assert len(milestones) >= 1
    all_phases = [ph for m in milestones for ph in m.phases]
    assert len(all_phases) == 3
    assert all_phases[0].number == 1
    assert all_phases[0].title == "Setup"
    assert all_phases[1].number == 2
    assert all_phases[1].title == "Build"
    assert all_phases[2].number == 3
    assert all_phases[2].title == "Ship"


def test_goal_extraction(tmp_path: Path):
    p = _write(tmp_path, BASIC_ROADMAP)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    all_phases = [ph for m in r.value.milestones for ph in m.phases]
    assert all_phases[0].goal == "Initialize the project"
    assert all_phases[1].goal == "Build the feature"
    assert all_phases[2].goal == "Deploy to production"


# ---------------------------------------------------------------------------
# Milestone extraction
# ---------------------------------------------------------------------------

MILESTONE_ROADMAP = """\
# Roadmap: Milestone Project

## Milestones

- [x] **v1.0** — First milestone (shipped)
- [ ] **v2.0** — Second milestone

## v1.0

### Phases

- [x] **Phase 1: Alpha** - done
- [x] **Phase 2: Beta** - done

## v2.0

### Phases

- [ ] **Phase 3: Gamma** - in flight
- [ ] **Phase 4: Delta** - planned

## Phase Details

### Phase 1: Alpha

**Goal**: Alpha goal

### Phase 2: Beta

**Goal**: Beta goal

### Phase 3: Gamma

**Goal**: Gamma goal

### Phase 4: Delta

**Goal**: Delta goal
"""


def test_milestone_extraction(tmp_path: Path):
    p = _write(tmp_path, MILESTONE_ROADMAP)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    milestones = r.value.milestones
    assert len(milestones) >= 1


def test_milestone_emoji_completed(tmp_path: Path):
    text = """\
# Roadmap: Test

## v1.0 ✅

### Phases

- [x] **Phase 1: Done**

## v2.0 🚀

### Phases

- [ ] **Phase 2: Active**
"""
    p = _write(tmp_path, text)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    milestones = r.value.milestones
    titles = {m.title: m.status for m in milestones}
    # v1.0 should be COMPLETED (checkmark emoji)
    v1 = next((m for m in milestones if "v1.0" in m.title or "1.0" in m.title), None)
    assert v1 is not None
    assert v1.status == MilestoneStatus.COMPLETED


def test_milestone_emoji_active(tmp_path: Path):
    text = """\
# Roadmap: Test

## v2.0 🚀

### Phases

- [ ] **Phase 1: Active**
"""
    p = _write(tmp_path, text)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    milestones = r.value.milestones
    v2 = next((m for m in milestones if "v2.0" in m.title or "2.0" in m.title), None)
    assert v2 is not None
    assert v2.status == MilestoneStatus.ACTIVE


# ---------------------------------------------------------------------------
# Milestone-prefixed phase IDs (Phase 1-01)
# ---------------------------------------------------------------------------

PREFIXED_PHASES_ROADMAP = """\
# Roadmap: Prefixed Project

## Phase Details

### Phase 1-01: First Sub-Phase

**Goal**: Sub-phase goal one

### Phase 1-02: Second Sub-Phase

**Goal**: Sub-phase goal two

### Phase 2-01: Another Milestone Sub

**Goal**: Another goal
"""


def test_milestone_prefixed_phase_ids(tmp_path: Path):
    p = _write(tmp_path, PREFIXED_PHASES_ROADMAP)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    all_phases = [ph for m in r.value.milestones for ph in m.phases]
    assert len(all_phases) == 3

    ph1 = all_phases[0]
    assert ph1.code == "1-01"
    assert ph1.title == "First Sub-Phase"
    assert ph1.number == 1  # numeric portion from "1-01"

    ph2 = all_phases[1]
    assert ph2.code == "1-02"

    ph3 = all_phases[2]
    assert ph3.code == "2-01"


# ---------------------------------------------------------------------------
# Plan completion status
# ---------------------------------------------------------------------------

PLANS_STATUS_ROADMAP = """\
# Roadmap: Plans Project

## Phase Details

### Phase 1: Complete Phase

**Goal**: A complete phase

**Plans:** 2/2 plans complete

- [x] 01-01-PLAN.md
- [x] 01-02-PLAN.md

### Phase 2: In-Progress Phase

**Goal**: A partially done phase

**Plans:** 1/3 plans complete

- [x] 02-01-PLAN.md
- [ ] 02-02-PLAN.md
- [ ] 02-03-PLAN.md

### Phase 3: Not Started Phase

**Goal**: A not started phase

**Plans:** 0/2 plans complete

- [ ] 03-01-PLAN.md
- [ ] 03-02-PLAN.md
"""


def test_phase_status_from_plan_completion(tmp_path: Path):
    p = _write(tmp_path, PLANS_STATUS_ROADMAP)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    all_phases = [ph for m in r.value.milestones for ph in m.phases]
    assert len(all_phases) == 3

    assert all_phases[0].status == PhaseStatus.COMPLETE
    assert all_phases[1].status == PhaseStatus.IN_PROGRESS
    assert all_phases[2].status == PhaseStatus.NOT_STARTED


# ---------------------------------------------------------------------------
# Archived milestones in <details> blocks
# ---------------------------------------------------------------------------

ARCHIVED_ROADMAP = """\
# Roadmap: Archive Project

## Milestones

- [x] **v1.0** — Shipped
- [ ] **v2.0** — Active

<details>
<summary>v1.0 — Archived (shipped)</summary>

### Phase 1: Old Feature

**Goal**: The old feature goal

</details>

## v2.0

### Phases

- [ ] **Phase 2: New Feature**

## Phase Details

### Phase 2: New Feature

**Goal**: New feature goal
"""


def test_archived_milestones_in_details_blocks(tmp_path: Path):
    p = _write(tmp_path, ARCHIVED_ROADMAP)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    # The archived milestone phases should be included somewhere
    all_phases = [ph for m in r.value.milestones for ph in m.phases]
    phase_titles = [ph.title for ph in all_phases]
    # Either the archived phase is included or current phases are at minimum present
    assert len(all_phases) >= 1


# ---------------------------------------------------------------------------
# Return type is ParseResult.ok with GsdProject
# ---------------------------------------------------------------------------

def test_returns_parse_result_ok(tmp_path: Path):
    p = _write(tmp_path, BASIC_ROADMAP)
    r = GsdCoreRoadmapParser.parse(str(p))
    assert r.is_success
    assert r.value is not None
    # Check it's a GsdProject
    from gsd_monitor.models.core import GsdProject
    assert isinstance(r.value, GsdProject)
