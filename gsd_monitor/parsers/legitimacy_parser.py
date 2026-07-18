"""Package Legitimacy Audit parser — extracts flagged packages from RESEARCH.md."""

from __future__ import annotations

import re

# Heading that starts the legitimacy audit section
_SECTION_HDR = re.compile(
    r"^#{1,4}\s+Package\s+Legitimacy\s+Audit\s*$",
    re.MULTILINE | re.IGNORECASE,
)

# Next ## or higher heading (to bound the section)
_NEXT_SECTION = re.compile(r"^#{1,4}\s+\S", re.MULTILINE)

# Markdown table row: | package-name | ... | <legitimacy-signal> | ... |
# Captures first column (package name) and the entire row
_TABLE_ROW = re.compile(
    r"^\|\s*([^|]+?)\s*\|(?:[^|\n]*\|)*\s*$",
    re.MULTILINE,
)

# Signals that indicate a flagged/suspicious package
_FLAGGED_SIGNALS = re.compile(
    r"❌|⚠️|suspicious|unknown|flagged|unverified|typosquat",
    re.IGNORECASE,
)

# Signals that indicate a clearly legitimate package (skip these)
_LEGITIMATE_SIGNALS = re.compile(
    r"✅|legitimate|verified|ok\b|well.?known",
    re.IGNORECASE,
)

# Table separator row (|---|---|) — skip
_SEPARATOR_ROW = re.compile(r"^\|[\s\-|]+\|$")


class LegitimacyParser:
    @staticmethod
    def parse(text: str) -> list[str]:
        """Extract flagged package names from a RESEARCH.md Package Legitimacy Audit section.

        Args:
            text: Raw text content of a RESEARCH.md file.

        Returns:
            List of flagged package name strings. Empty list if no section or no flagged packages.
        """
        if not text:
            return []

        # Find the section
        section_m = _SECTION_HDR.search(text)
        if not section_m:
            return []

        # Bound section to next heading
        section_start = section_m.end()
        next_m = _NEXT_SECTION.search(text, section_start)
        section_text = text[section_start:next_m.start()] if next_m else text[section_start:]

        flagged: list[str] = []
        for row_m in _TABLE_ROW.finditer(section_text):
            row = row_m.group(0)
            # Skip separator rows
            if _SEPARATOR_ROW.match(row.strip()):
                continue
            # Skip header row (first column is typically "Package" or similar label)
            pkg_name = row_m.group(1).strip()
            if not pkg_name or pkg_name.lower() in ("package", "name", "library", "dependency"):
                continue
            # A row is flagged if it contains a flagged signal AND no legitimate signal
            # (legitimate signal overrides — a row can't be both)
            if _FLAGGED_SIGNALS.search(row) and not _LEGITIMATE_SIGNALS.search(row):
                flagged.append(pkg_name)

        return flagged
