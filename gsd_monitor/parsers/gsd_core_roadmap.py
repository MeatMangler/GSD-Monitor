"""ROADMAP.md parser — gsd-core heading-based format."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from gsd_monitor.models.core import GsdProject, Milestone, ParseResult, PhaseEntry
from gsd_monitor.models.enums import GsdVersion, MilestoneStatus, PhaseStatus

logger = logging.getLogger(__name__)

# Match "## Phase N: Title" or "### Phase N: Title"
# Supports plain integers (Phase 1), milestone-prefixed IDs (Phase 1-01),
# and backlog/dot-separated IDs (Phase 999.1)
_HEADING_PHASE = re.compile(
    r"^#{2,3} Phase ([\d]+(?:[.\-][\d]+)?): (.+)",
    re.MULTILINE,
)

# Milestone headings: "## v1.0" or "## v1.0 ✅" or "## v2.0 🚀"
# Must look like a semver-ish string (vN.N...) to avoid matching "## Phase Details"
_MILESTONE_HDR = re.compile(
    r"^## (v[\d]+\.[\d]+[^\r\n]*)",
    re.MULTILINE,
)

# Emoji/marker patterns for milestone status
_EMOJI_COMPLETED = re.compile(r"[✅✓☑✔]|completed?|shipped|done|archived", re.IGNORECASE)
_EMOJI_ACTIVE = re.compile(r"[🚀🔨🔧⚙️🏗️]|active|in.progress|current", re.IGNORECASE)

# Goal line: "**Goal**: text" or "**Goal:** text"
_GOAL = re.compile(r"\*\*Goal\*\*:?\s*(.+)")

# Plan completion header: "**Plans:** N/M plans complete"
_PLANS_HEADER = re.compile(r"\*\*Plans:\*\*\s*(\d+)/(\d+)")

# Plan checkbox lines within a phase section
_PLAN_CHECKED = re.compile(r"^- \[x\]", re.MULTILINE | re.IGNORECASE)
_PLAN_UNCHECKED = re.compile(r"^- \[ \]", re.MULTILINE)

# Checkbox-style phase line within milestone Phases section
# e.g. "- [x] **Phase 1: Title**" or "- [ ] **Phase 999.1: Title**"
_CHECKBOX_PHASE = re.compile(
    r"^- \[([x ])\] \*\*Phase ([\d]+(?:[.\-][\d]+)?): ([^*]+)\*\*",
    re.MULTILINE,
)

# <details> open tag to detect archived milestone blocks
_DETAILS_OPEN = re.compile(r"<details>", re.IGNORECASE)
_DETAILS_CLOSE = re.compile(r"</details>", re.IGNORECASE)

# Extract completion date from summary text: "SHIPPED 2026-04-12" or "SHIPPED: 2026-04-12"
_SHIPPED_DATE = re.compile(r"SHIPPED\s+(\d{4}-\d{2}-\d{2})")

# "## Phase Details" section marker
_PHASE_DETAILS_HDR = re.compile(r"^## Phase Details\s*$", re.MULTILINE | re.IGNORECASE)


def _parse_phase_id(raw_id: str) -> tuple[int, str | None]:
    """Parse a phase ID string into (number, code).

    Args:
        raw_id: The ID string from the heading — "5", "1-01", or "999.1".

    Returns:
        Tuple of (numeric_part, code) where code is None for plain integers
        and the full string for milestone-prefixed or dot-separated IDs.
    """
    if "-" in raw_id:
        # Milestone-prefixed: "1-01" → number=1, code="1-01"
        prefix = raw_id.split("-")[0]
        try:
            return int(prefix), raw_id
        except ValueError:
            return 0, raw_id
    if "." in raw_id:
        # Dot-separated backlog: "999.1" → number=999, code="999.1"
        prefix = raw_id.split(".")[0]
        try:
            return int(prefix), raw_id
        except ValueError:
            return 0, raw_id
    try:
        return int(raw_id), None
    except ValueError:
        return 0, None


def _determine_phase_status_from_section(section_text: str) -> PhaseStatus:
    """Determine phase status from the content of a phase section."""
    ph = _PLANS_HEADER.search(section_text)
    if ph:
        completed = int(ph.group(1))
        total = int(ph.group(2))
        if total == 0:
            return PhaseStatus.NOT_STARTED
        if completed == total:
            return PhaseStatus.COMPLETE
        if completed > 0:
            return PhaseStatus.IN_PROGRESS
        return PhaseStatus.NOT_STARTED

    # Fall back to checkbox counting
    checked = len(_PLAN_CHECKED.findall(section_text))
    unchecked = len(_PLAN_UNCHECKED.findall(section_text))
    if checked > 0 and unchecked == 0:
        return PhaseStatus.COMPLETE
    if checked > 0:
        return PhaseStatus.IN_PROGRESS
    return PhaseStatus.NOT_STARTED


def _determine_milestone_status(title_line: str, phases: list[PhaseEntry]) -> MilestoneStatus:
    """Determine milestone status from emoji markers or phase completion."""
    if _EMOJI_COMPLETED.search(title_line):
        return MilestoneStatus.COMPLETED
    if _EMOJI_ACTIVE.search(title_line):
        return MilestoneStatus.ACTIVE

    # Derive from phases if no explicit marker
    if not phases:
        return MilestoneStatus.PLANNED
    completed = sum(1 for p in phases if p.status == PhaseStatus.COMPLETE)
    if completed == len(phases):
        return MilestoneStatus.COMPLETED
    if completed > 0:
        return MilestoneStatus.ACTIVE
    return MilestoneStatus.PLANNED


def _extract_phases_from_section(text: str, start: int, end: int) -> list[tuple[str, str, PhaseStatus]]:
    """Extract phases from a section bounded by [start, end) in text.

    Returns list of (raw_id, title, status) tuples.
    """
    section = text[start:end]
    results = []

    # Try checkbox-style phase lines first (common in Phases lists within milestones)
    for m in _CHECKBOX_PHASE.finditer(section):
        checked = m.group(1).lower() == "x"
        raw_id = m.group(2)
        title = m.group(3).strip()
        status = PhaseStatus.COMPLETE if checked else PhaseStatus.NOT_STARTED
        results.append((raw_id, title, status))

    return results


class GsdCoreRoadmapParser:
    """Parser for gsd-core heading-based ROADMAP.md format."""

    @staticmethod
    def parse(file_path: str) -> ParseResult:
        try:
            p = Path(file_path)
            if not p.is_file():
                return ParseResult.err(f"ROADMAP.md not found: {file_path}")
            text = p.read_text(encoding="utf-8", errors="replace")
            parent = str(p.parent)
            project_name = GsdCoreRoadmapParser._extract_project_name(text, file_path)

            # Strategy: Parse "## Phase Details" section for authoritative phase list,
            # then build milestones from "## vX.Y" headings that reference those phases.
            milestones = GsdCoreRoadmapParser._parse_milestones(text)

            return ParseResult.ok(
                GsdProject(
                    name=project_name,
                    path=parent,
                    milestones=milestones,
                    version=GsdVersion.CORE,
                )
            )
        except Exception as ex:
            return ParseResult.err(f"Failed to parse gsd-core ROADMAP.md: {ex}")

    @staticmethod
    def _extract_project_name(text: str, file_path: str) -> str:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("# "):
                name = line[2:].strip()
                if name.lower().startswith("roadmap:"):
                    name = name[8:].strip()
                if name:
                    return name
        return Path(file_path).parent.name or "Unknown"

    @staticmethod
    def _parse_milestones(text: str) -> list[Milestone]:
        """Parse milestones and their phases from the full ROADMAP text."""

        # First, build a complete map of all phase definitions from "## Phase Details"
        phase_map = GsdCoreRoadmapParser._extract_phase_details(text)

        # Find milestone headings (## vX.Y ...)
        ms_matches = list(_MILESTONE_HDR.finditer(text))

        if not ms_matches:
            # No milestone headings — check for standalone phase details section
            if phase_map:
                phases = list(phase_map.values())
                any_complete = any(p.status == PhaseStatus.COMPLETE for p in phases)
                any_active = any(p.status == PhaseStatus.IN_PROGRESS for p in phases)
                if any_complete and any(p.status != PhaseStatus.COMPLETE for p in phases):
                    ms_status = MilestoneStatus.ACTIVE
                elif any_complete:
                    ms_status = MilestoneStatus.COMPLETED
                elif any_active:
                    ms_status = MilestoneStatus.ACTIVE
                else:
                    ms_status = MilestoneStatus.PLANNED
                return [
                    Milestone(
                        number=1,
                        title="v1.0",
                        status=ms_status,
                        phases=phases,
                    )
                ]
            return []

        milestones: list[Milestone] = []
        ms_count = 0

        # Also look for archived milestones in <details> blocks
        archived = GsdCoreRoadmapParser._extract_archived_milestones(text, phase_map)

        for i, ms_m in enumerate(ms_matches):
            ms_title_line = ms_m.group(1).strip()
            ms_title = re.sub(r"\s+[^\w\s].*$", "", ms_title_line).strip()
            # Clean up emoji from title
            ms_title = re.sub(r"\s*[✅✓☑✔🚀🔨🔧⚙️🏗️]\s*.*$", "", ms_title).strip()

            # Find the text region for this milestone section
            region_start = ms_m.end()
            region_end = ms_matches[i + 1].start() if i + 1 < len(ms_matches) else len(text)
            region = text[region_start:region_end]

            # Collect phases referenced in this milestone's Phases list
            phase_entries = GsdCoreRoadmapParser._collect_milestone_phases(
                region, ms_title_line, phase_map
            )

            ms_status = _determine_milestone_status(ms_title_line, phase_entries)
            ms_count += 1
            milestones.append(
                Milestone(
                    number=ms_count,
                    title=ms_title,
                    status=ms_status,
                    phases=phase_entries,
                )
            )

        # Add archived milestones at the end
        for arch_ms in archived:
            ms_count += 1
            milestones.append(
                Milestone(
                    number=ms_count,
                    title=arch_ms.title,
                    status=arch_ms.status,
                    phases=arch_ms.phases,
                    is_archived=arch_ms.is_archived,
                    completion_date=arch_ms.completion_date,
                )
            )

        return milestones

    @staticmethod
    def _collect_milestone_phases(
        region_text: str,
        ms_title_line: str,
        phase_map: dict[str, PhaseEntry],
    ) -> list[PhaseEntry]:
        """Collect phases for a milestone from its section text."""
        phases: list[PhaseEntry] = []

        # Look for checkbox-style phase lines in this region
        for m in _CHECKBOX_PHASE.finditer(region_text):
            checked = m.group(1).lower() == "x"
            raw_id = m.group(2)
            title = m.group(3).strip()
            checkbox_status = PhaseStatus.COMPLETE if checked else PhaseStatus.NOT_STARTED

            # Look up the full phase definition from the phase map
            if raw_id in phase_map:
                ph = phase_map[raw_id]
                # Merge: use checkbox status if phase map has NOT_STARTED, else keep map status
                if ph.status == PhaseStatus.NOT_STARTED and checkbox_status == PhaseStatus.COMPLETE:
                    ph = ph.model_copy(update={"status": checkbox_status})
                phases.append(ph)
            else:
                number, code = _parse_phase_id(raw_id)
                phases.append(
                    PhaseEntry(
                        number=number,
                        code=code,
                        title=title,
                        status=checkbox_status,
                    )
                )

        return phases

    @staticmethod
    def _extract_phase_details(text: str) -> dict[str, PhaseEntry]:
        """Extract the authoritative phase list from the '## Phase Details' section.

        Returns a dict mapping raw_id -> PhaseEntry.
        """
        phase_map: dict[str, PhaseEntry] = {}

        # Find the "## Phase Details" heading
        details_m = _PHASE_DETAILS_HDR.search(text)
        if not details_m:
            # No Phase Details section — try to find phases from any ### Phase headings
            section_text = text
        else:
            section_text = text[details_m.end():]

        # Find all "### Phase N: Title" or "## Phase N: Title" headings in this section
        phase_matches = list(_HEADING_PHASE.finditer(section_text))
        if not phase_matches:
            return phase_map

        for i, m in enumerate(phase_matches):
            raw_id = m.group(1)
            title = m.group(2).strip()
            number, code = _parse_phase_id(raw_id)

            # Extract the body of this phase section
            body_start = m.end()
            body_end = phase_matches[i + 1].start() if i + 1 < len(phase_matches) else len(section_text)
            body = section_text[body_start:body_end]

            # Extract goal
            gm = _GOAL.search(body)
            goal = gm.group(1).strip() if gm else None

            # Determine status from plan completions in the body
            status = _determine_phase_status_from_section(body)

            phase_map[raw_id] = PhaseEntry(
                number=number,
                code=code,
                title=title,
                goal=goal,
                status=status,
            )

        return phase_map

    @staticmethod
    def _extract_archived_milestones(
        text: str, phase_map: dict[str, PhaseEntry]
    ) -> list[Milestone]:
        """Extract milestone entries from <details> archived blocks."""
        archived: list[Milestone] = []

        # Find all <details>...</details> blocks
        detail_opens = list(_DETAILS_OPEN.finditer(text))
        detail_closes = list(_DETAILS_CLOSE.finditer(text))

        for open_m in detail_opens:
            # Find matching close tag
            close_m = next(
                (c for c in detail_closes if c.start() > open_m.end()),
                None,
            )
            if not close_m:
                continue

            block = text[open_m.end():close_m.start()]

            # Extract summary title
            summary_m = re.search(r"<summary>([^<]+)</summary>", block, re.IGNORECASE)
            if not summary_m:
                continue
            summary_title = summary_m.group(1).strip()

            # Extract phases from the block
            phase_entries: list[PhaseEntry] = []
            for m in _HEADING_PHASE.finditer(block):
                raw_id = m.group(1)
                title = m.group(2).strip()
                number, code = _parse_phase_id(raw_id)

                # Look up in phase_map for enriched data
                if raw_id in phase_map:
                    phase_entries.append(phase_map[raw_id])
                else:
                    phase_entries.append(
                        PhaseEntry(number=number, code=code, title=title)
                    )

            if not phase_entries:
                # Try checkbox-style within block
                for m in _CHECKBOX_PHASE.finditer(block):
                    checked = m.group(1).lower() == "x"
                    raw_id = m.group(2)
                    title = m.group(3).strip()
                    number, code = _parse_phase_id(raw_id)
                    if raw_id in phase_map:
                        phase_entries.append(phase_map[raw_id])
                    else:
                        phase_entries.append(
                            PhaseEntry(
                                number=number,
                                code=code,
                                title=title,
                                status=PhaseStatus.COMPLETE if checked else PhaseStatus.NOT_STARTED,
                            )
                        )

            if phase_entries:
                ms_status = _determine_milestone_status(summary_title, phase_entries)
                shipped_m = _SHIPPED_DATE.search(summary_title)
                completion_date = shipped_m.group(1) if shipped_m else None
                archived.append(
                    Milestone(
                        number=0,  # Will be renumbered by caller
                        title=summary_title,
                        status=ms_status,
                        phases=phase_entries,
                        is_archived=True,
                        completion_date=completion_date,
                    )
                )

        return archived
