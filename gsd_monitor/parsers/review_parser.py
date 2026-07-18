"""Code review findings parser — extracts severity counts from XX-REVIEW.md files."""

from __future__ import annotations

import re

from gsd_monitor.models.core import ReviewSummary

# Table row: | Critical | 3 |  or  | Warning | 1 |
_TABLE_ROW = re.compile(
    r"^\|\s*(critical|warning|info)\s*\|\s*(\d+)\s*\|",
    re.MULTILINE | re.IGNORECASE,
)

# Heading-based severity section: ## Critical  or  ## Critical Findings
_HEADING_SEVERITY = re.compile(
    r"^#{1,4}\s+(critical|warning|info)(?:\s+findings?)?\s*$",
    re.MULTILINE | re.IGNORECASE,
)

# Bullet finding under a severity heading: lines starting with "- "
_BULLET = re.compile(r"^\s*-\s+\S", re.MULTILINE)

# Next heading at same or higher level
_ANY_HEADING = re.compile(r"^#{1,4}\s+\S", re.MULTILINE)


class ReviewParser:
    @staticmethod
    def parse(text: str) -> ReviewSummary | None:
        """Extract severity counts from a REVIEW.md file.

        Tries table format first (| Critical | N |), then counts bullets under
        severity headings (## Critical / ## Warning / ## Info).

        Returns:
            ReviewSummary with counts, or None if text is empty.
            Returns ReviewSummary(0, 0, 0) if file exists but has no counts.
        """
        if not text:
            return None

        critical = warning = info = 0
        found_table = False

        # Pass 1: table format
        for m in _TABLE_ROW.finditer(text):
            sev = m.group(1).lower()
            count = int(m.group(2))
            if sev == "critical":
                critical += count
                found_table = True
            elif sev == "warning":
                warning += count
                found_table = True
            elif sev == "info":
                info += count
                found_table = True

        if found_table:
            return ReviewSummary(critical=critical, warning=warning, info=info)

        # Pass 2: count bullets under severity headings
        headings = list(_HEADING_SEVERITY.finditer(text))
        for i, hm in enumerate(headings):
            sev = hm.group(1).lower()
            # Find text block until the next heading (any level)
            block_start = hm.end()
            # Find next heading after block_start
            next_hdr = None
            for nm in _ANY_HEADING.finditer(text[block_start:]):
                next_hdr = block_start + nm.start()
                break
            block = text[block_start:next_hdr] if next_hdr else text[block_start:]
            count = len(_BULLET.findall(block))
            if sev == "critical":
                critical += count
            elif sev == "warning":
                warning += count
            elif sev == "info":
                info += count

        return ReviewSummary(critical=critical, warning=warning, info=info)
