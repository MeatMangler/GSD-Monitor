"""REQUIREMENTS.md parser — extracts requirements with category and traceability data."""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field


# Category heading: "### Detection & Parsing" or "### Enhanced Visibility"
_CATEGORY_HDR = re.compile(r"^###\s+(.+)$", re.MULTILINE)

# Top-level section heading (##) — used to bound the v3.0 section
_SECTION_HDR = re.compile(r"^##\s+(.+)$", re.MULTILINE)

# Requirement line: "- [x] **DETECT-01**: description" or "- [ ] **VIS-01**: description"
_REQ_LINE = re.compile(
    r"^-\s+\[([x ])\]\s+\*\*([A-Z][A-Z0-9]+-\d+)\*\*:\s+(.+)$",
    re.MULTILINE | re.IGNORECASE,
)

# Traceability table row: "| DETECT-01 | Phase 11 | Complete |"
# Handles leading/trailing whitespace in cells
_TRACE_ROW = re.compile(
    r"^\|\s*([A-Z][A-Z0-9]+-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",
    re.MULTILINE | re.IGNORECASE,
)

# Traceability section header
_TRACE_SECTION = re.compile(r"^##\s+Traceability\s*$", re.MULTILINE | re.IGNORECASE)

# v3.0 requirements section header
_V3_SECTION = re.compile(r"^##\s+v3\.0\s+Requirements\s*$", re.MULTILINE | re.IGNORECASE)


class RequirementEntry(BaseModel):
    id: str = ""
    category: str = ""
    description: str = ""
    is_checked: bool = False
    phase: str | None = None
    status: str | None = None
    is_gap: bool = False


class RequirementsParser:
    @staticmethod
    def parse(planning_dir: str) -> list[RequirementEntry]:
        """Parse REQUIREMENTS.md from planning_dir, returning all requirement entries.

        Args:
            planning_dir: Path to the .planning/ directory (or directory containing REQUIREMENTS.md).

        Returns:
            List of RequirementEntry objects. Returns empty list if REQUIREMENTS.md not found.
        """
        req_file = Path(planning_dir) / "REQUIREMENTS.md"
        if not req_file.is_file():
            return []

        try:
            text = req_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return []

        # --- Pass 1: Build traceability map from the ## Traceability section ---
        trace_map: dict[str, tuple[str, str]] = {}
        trace_m = _TRACE_SECTION.search(text)
        if trace_m:
            trace_section = text[trace_m.end():]
            for row in _TRACE_ROW.finditer(trace_section):
                req_id = row.group(1).strip()
                phase = row.group(2).strip()
                status = row.group(3).strip()
                trace_map[req_id] = (phase, status)

        # --- Pass 2: Bound the search to the "## v3.0 Requirements" section only ---
        # Requirements in "## Validated" or "## Future Requirements" sections are not
        # v3.0 spec items and must not be included in the output.
        v3_m = _V3_SECTION.search(text)
        if v3_m:
            # Find the next ## section heading after v3.0 — that marks the end
            v3_start = v3_m.end()
            next_section = None
            for sec_m in _SECTION_HDR.finditer(text):
                if sec_m.start() > v3_m.start():
                    next_section = sec_m
                    break
            v3_end = next_section.start() if next_section else len(text)
            req_text = text[v3_start:v3_end]
            req_text_offset = v3_start
        else:
            # No v3.0 section found — scan entire file
            req_text = text
            req_text_offset = 0

        # Build a sorted list of (position, category) pairs within the bounded region
        category_positions: list[tuple[int, str]] = []
        for cat_m in _CATEGORY_HDR.finditer(req_text):
            category_positions.append((cat_m.start(), cat_m.group(1).strip()))

        entries: list[RequirementEntry] = []
        for req_m in _REQ_LINE.finditer(req_text):
            req_pos = req_m.start()
            is_checked = req_m.group(1).lower() == "x"
            req_id = req_m.group(2).strip()
            description = req_m.group(3).strip()

            # Determine category: find the last category heading before this requirement
            category = ""
            for cat_pos, cat_name in category_positions:
                if cat_pos <= req_pos:
                    category = cat_name
                else:
                    break

            # Look up traceability
            phase: str | None = None
            status: str | None = None
            is_gap = False
            if req_id in trace_map:
                phase, status = trace_map[req_id]
            else:
                is_gap = True

            entries.append(
                RequirementEntry(
                    id=req_id,
                    category=category,
                    description=description,
                    is_checked=is_checked,
                    phase=phase,
                    status=status,
                    is_gap=is_gap,
                )
            )

        return entries
