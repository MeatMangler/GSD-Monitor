"""CONTEXT.md decision parser — extracts D-XX decision entries."""

from __future__ import annotations

import re

from gsd_monitor.models.core import DecisionEntry

# Matches: - **D-01:** text  (colon inside bold)  or  - **D-01** text  (no colon)
# Also handles colon outside bold: - **D-01**: text
_DECISION_LINE = re.compile(
    r"^-\s+\*\*D-(\d+):?\*\*:?\s+(.+)$",
    re.MULTILINE,
)


class DecisionParser:
    @staticmethod
    def parse(text: str) -> list[DecisionEntry]:
        """Extract decision entries from CONTEXT.md content.

        Args:
            text: Raw text content of a CONTEXT.md file.

        Returns:
            List of DecisionEntry objects. Empty list if none found or text is empty.
        """
        if not text:
            return []
        entries: list[DecisionEntry] = []
        for m in _DECISION_LINE.finditer(text):
            num = m.group(1).lstrip("0") or "0"
            entries.append(
                DecisionEntry(
                    id=f"D-{num.zfill(2)}",
                    text=m.group(2).strip(),
                    is_covered=False,  # Coverage set by caller based on phase validation state
                )
            )
        return entries
