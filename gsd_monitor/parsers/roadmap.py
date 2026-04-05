"""ROADMAP.md parser — GSD-1 checkbox format and fallbacks."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from gsd_monitor.models.core import GsdProject, Milestone, ParseResult, PhaseEntry
from gsd_monitor.models.enums import MilestoneStatus, PhaseStatus

logger = logging.getLogger(__name__)


_GSD_PHASE = re.compile(
    r"^- \[([x ])\] \*\*Phase (\d+): ([^*]+)\*\*", re.MULTILINE
)
_SECTION_SPLIT = re.compile(r"^### Phase (\d+):", re.MULTILINE)
_GOAL = re.compile(r"\*\*Goal\*\*:\s*(.+)")
_ARCHIVE_PHASE = re.compile(r"^### Phase (\d+): (.+)", re.MULTILINE)
_ARCHIVE_STATUS = re.compile(r"^\*\*Status\*\*:\s*(.+)", re.MULTILINE)


class RoadmapParser:
    @staticmethod
    def parse(file_path: str) -> ParseResult:
        try:
            p = Path(file_path)
            if not p.is_file():
                return ParseResult.err(f"ROADMAP.md not found: {file_path}")
            text = p.read_text(encoding="utf-8", errors="replace")
            project_name = RoadmapParser._extract_project_name(text, file_path)
            milestones = RoadmapParser._try_extract_gsd_phases(text)
            if not milestones or all(len(m.phases) == 0 for m in milestones):
                arch = RoadmapParser._try_extract_from_milestone_archives(file_path)
                if arch:
                    milestones = arch
            parent = str(p.parent)
            return ParseResult.ok(
                GsdProject(name=project_name, path=parent, milestones=milestones)
            )
        except Exception as ex:
            return ParseResult.err(f"Failed to parse ROADMAP.md: {ex}")

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
    def _extract_phase_goals(text: str) -> dict[int, str]:
        goals: dict[int, str] = {}
        parts = _SECTION_SPLIT.split(text)
        for i in range(1, len(parts) - 1, 2):
            if i + 1 >= len(parts):
                break
            num_s = parts[i]
            section = parts[i + 1]
            try:
                phase_num = int(num_s)
            except ValueError:
                continue
            gm = _GOAL.search(section)
            if gm:
                goals[phase_num] = gm.group(1).strip()
        return goals

    @staticmethod
    def _try_extract_gsd_phases(text: str) -> list[Milestone] | None:
        matches = list(_GSD_PHASE.finditer(text))
        if not matches:
            return None
        goals = RoadmapParser._extract_phase_goals(text)
        phases: list[PhaseEntry] = []
        for m in matches:
            complete = m.group(1) == "x"
            number = int(m.group(2))
            title = m.group(3).strip()
            phases.append(
                PhaseEntry(
                    number=number,
                    title=title,
                    status=PhaseStatus.COMPLETE if complete else PhaseStatus.NOT_STARTED,
                    goal=goals.get(number),
                )
            )
        any_complete = any(p.status == PhaseStatus.COMPLETE for p in phases)
        any_incomplete = any(p.status == PhaseStatus.NOT_STARTED for p in phases)
        if any_complete and any_incomplete:
            idx = next(i for i, p in enumerate(phases) if p.status == PhaseStatus.NOT_STARTED)
            p = phases[idx]
            phases[idx] = PhaseEntry(
                number=p.number,
                title=p.title,
                status=PhaseStatus.IN_PROGRESS,
                goal=p.goal,
            )
        completed = sum(1 for p in phases if p.status == PhaseStatus.COMPLETE)
        if len(phases) == 0:
            ms = MilestoneStatus.PLANNED
        elif completed == len(phases):
            ms = MilestoneStatus.COMPLETED
        elif completed > 0:
            ms = MilestoneStatus.ACTIVE
        else:
            ms = MilestoneStatus.PLANNED
        return [
            Milestone(
                number=1,
                title="v1.0",
                status=ms,
                phases=phases,
            )
        ]

    @staticmethod
    def _try_extract_from_milestone_archives(main_roadmap_path: str) -> list[Milestone] | None:
        try:
            main = Path(main_roadmap_path)
            planning_dir = main.parent
            milestones_dir = planning_dir / "milestones"
            if not milestones_dir.is_dir():
                return None
            roadmap_files = sorted(milestones_dir.glob("*-ROADMAP.md"))
            if not roadmap_files:
                return None
            out: list[Milestone] = []
            milestone_number = 0
            for roadmap_file in roadmap_files:
                stem = roadmap_file.stem
                version = stem[: -len("-ROADMAP")] if stem.lower().endswith("-roadmap") else stem
                text = roadmap_file.read_text(encoding="utf-8", errors="replace")
                parsed = RoadmapParser._try_extract_gsd_phases(text)
                all_phases = [ph for m in parsed for ph in m.phases] if parsed else []
                if not all_phases:
                    all_phases = RoadmapParser._try_extract_archive_phases(text) or []
                if not all_phases:
                    continue
                milestone_number += 1
                completed = sum(1 for p in all_phases if p.status == PhaseStatus.COMPLETE)
                if completed == len(all_phases):
                    st = MilestoneStatus.COMPLETED
                elif completed > 0:
                    st = MilestoneStatus.ACTIVE
                else:
                    st = MilestoneStatus.PLANNED
                out.append(
                    Milestone(
                        number=milestone_number,
                        title=version,
                        status=st,
                        phases=all_phases,
                    )
                )
            return out if out else None
        except Exception as ex:
            logger.warning("Failed to extract milestone archives from %s: %s", main_roadmap_path, ex)
            return None

    @staticmethod
    def _try_extract_archive_phases(text: str) -> list[PhaseEntry] | None:
        matches = list(_ARCHIVE_PHASE.finditer(text))
        if not matches:
            return None
        phases: list[PhaseEntry] = []
        for i, m in enumerate(matches):
            number_s = m.group(1)
            title = m.group(2).strip()
            body_start = m.end()
            body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[body_start:body_end]
            try:
                number = int(number_s)
            except ValueError:
                continue
            gm = _GOAL.search(body)
            goal = gm.group(1).strip() if gm else None
            sm = _ARCHIVE_STATUS.search(body)
            status_text = sm.group(1).strip().lower() if sm else ""
            if "complete" in status_text:
                status = PhaseStatus.COMPLETE
            elif "in progress" in status_text or "in_progress" in status_text:
                status = PhaseStatus.IN_PROGRESS
            else:
                checked = len(re.findall(r"^- \[x\]", body, re.MULTILINE))
                unchecked = len(re.findall(r"^- \[ \]", body, re.MULTILINE))
                if checked > 0 and unchecked == 0:
                    status = PhaseStatus.COMPLETE
                elif checked > 0:
                    status = PhaseStatus.IN_PROGRESS
                else:
                    status = PhaseStatus.NOT_STARTED
            phases.append(PhaseEntry(number=number, title=title, status=status, goal=goal))
        return phases if phases else None

    @staticmethod
    def _extract_milestones_fallback(text: str) -> list[Milestone]:
        milestones: list[Milestone] = []
        number = 0
        for line in text.splitlines():
            if line.startswith("## "):
                title = line[3:].strip()
                if title:
                    number += 1
                    milestones.append(Milestone(number=number, title=title, status=MilestoneStatus.PLANNED))
        return milestones
