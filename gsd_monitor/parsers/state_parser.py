"""STATE.md / state.md parser."""

from __future__ import annotations

import re
from pathlib import Path

from gsd_monitor.models.core import ParseResult, StateInfo


_ACTIVE_MILESTONE = re.compile(r"\*\*Active Milestone:\*\*\s*([^\r\n]+)")
_ACTIVE_SLICE = re.compile(r"\*\*Active Slice:\*\*\s*([^\r\n]+)")
_ACTIVE_TASK = re.compile(r"\*\*Active Task:\*\*\s*([^\r\n]+)")
_WORKFLOW_PHASE = re.compile(r"\*\*Phase:\*\*\s*([^\r\n]+)")

# Bold inline progress fields.
# Supports both colon-inside "**total_phases:** 8" and colon-outside "**total_phases**: 8"
_BOLD_TOTAL = re.compile(r"\*\*total_phases:?\*\*:?\s*(\d+)")
_BOLD_COMPLETED = re.compile(r"\*\*completed_phases:?\*\*:?\s*(\d+)")
_BOLD_PERCENT = re.compile(r"\*\*progress_percent:?\*\*:?\s*(\d+)")

# Pipe-table rows: "| total_phases | 8 |" or "| total_phases | 8 |"
# Also accept "percent" as alias for progress_percent
_TABLE_TOTAL = re.compile(r"\|\s*total_phases\s*\|\s*(\d+)\s*\|")
_TABLE_COMPLETED = re.compile(r"\|\s*completed_phases\s*\|\s*(\d+)\s*\|")
_TABLE_PERCENT = re.compile(r"\|\s*(?:progress_percent|percent)\s*\|\s*(\d+)\s*\|")

# YAML frontmatter progress block (nested under "progress:" key)
_YAML_FRONTMATTER = re.compile(r"^---\s*\n(.*?)^---\s*\n", re.DOTALL | re.MULTILINE)


def _extract_yaml_int(yaml_text: str, key: str) -> int | None:
    """Extract an integer value from YAML text by key name."""
    pattern = re.compile(r"^\s+" + re.escape(key) + r":\s*(\d+)", re.MULTILINE)
    m = pattern.search(yaml_text)
    if m:
        return int(m.group(1))
    return None


def _extract_progress_from_frontmatter(text: str) -> tuple[int, int, int]:
    """Extract (total_phases, completed_phases, percent) from YAML frontmatter.

    Returns (0, 0, 0) if not found or not parseable.
    """
    fm = _YAML_FRONTMATTER.match(text)
    if not fm:
        return 0, 0, 0

    yaml_body = fm.group(1)

    # Look for the "progress:" key and extract nested fields
    progress_section_m = re.search(r"^progress:\s*\n((?:\s+\S[^\n]*\n?)*)", yaml_body, re.MULTILINE)
    if not progress_section_m:
        return 0, 0, 0

    progress_block = progress_section_m.group(1)

    total = _extract_yaml_int(progress_block, "total_phases") or 0
    completed = _extract_yaml_int(progress_block, "completed_phases") or 0
    percent = (
        _extract_yaml_int(progress_block, "percent")
        or _extract_yaml_int(progress_block, "progress_percent")
        or 0
    )
    return total, completed, percent


def _extract_progress(text: str) -> tuple[int, int, int]:
    """Extract (total_phases, completed_phases, progress_percent) from STATE.md text.

    Tries YAML frontmatter first, then bold-inline, then pipe-table.
    Returns (0, 0, 0) if no progress fields found.
    """
    # 1. YAML frontmatter
    total, completed, percent = _extract_progress_from_frontmatter(text)
    if total or completed or percent:
        return total, completed, percent

    # 2. Bold inline format: **total_phases:** 8
    t_m = _BOLD_TOTAL.search(text)
    c_m = _BOLD_COMPLETED.search(text)
    p_m = _BOLD_PERCENT.search(text)
    if t_m or c_m or p_m:
        return (
            int(t_m.group(1)) if t_m else 0,
            int(c_m.group(1)) if c_m else 0,
            int(p_m.group(1)) if p_m else 0,
        )

    # 3. Pipe-table format: | total_phases | 8 |
    t_m = _TABLE_TOTAL.search(text)
    c_m = _TABLE_COMPLETED.search(text)
    p_m = _TABLE_PERCENT.search(text)
    if t_m or c_m or p_m:
        return (
            int(t_m.group(1)) if t_m else 0,
            int(c_m.group(1)) if c_m else 0,
            int(p_m.group(1)) if p_m else 0,
        )

    return 0, 0, 0


class StateParser:
    @staticmethod
    def parse(file_path: str) -> ParseResult:
        try:
            p = Path(file_path)
            if not p.is_file():
                return ParseResult.err(f"STATE.md not found: {file_path}")
            text = p.read_text(encoding="utf-8", errors="replace")
            if not text.strip():
                return ParseResult.ok(StateInfo())

            total_phases, completed_phases, progress_percent = _extract_progress(text)

            if "# GSD State" in text:
                am = _ACTIVE_MILESTONE.search(text)
                as_ = _ACTIVE_SLICE.search(text)
                at = _ACTIVE_TASK.search(text)
                wp = _WORKFLOW_PHASE.search(text)
                return ParseResult.ok(
                    StateInfo(
                        active_milestone=am.group(1).strip() if am else None,
                        active_slice=as_.group(1).strip() if as_ else None,
                        active_task=at.group(1).strip() if at else None,
                        workflow_phase=wp.group(1).strip() if wp else None,
                        total_phases=total_phases,
                        completed_phases=completed_phases,
                        progress_percent=progress_percent,
                    )
                )
            status = StateParser._extract_current_position_text(text)
            return ParseResult.ok(
                StateInfo(
                    status=status,
                    total_phases=total_phases,
                    completed_phases=completed_phases,
                    progress_percent=progress_percent,
                )
            )
        except Exception as ex:
            return ParseResult.err(f"Failed to parse STATE.md: {ex}")

    @staticmethod
    def _extract_current_position_text(text: str) -> str:
        # Find ## ... Current Position ... or # ... Current Position
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if "Current Position" in line and line.strip().startswith("#"):
                # take first paragraph after heading
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith("#"):
                        break
                    if lines[j].strip():
                        return lines[j].strip()
                break
        return ""
