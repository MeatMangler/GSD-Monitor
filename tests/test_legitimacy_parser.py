"""Unit tests for LegitimacyParser."""

from __future__ import annotations

import pytest

from gsd_monitor.parsers.legitimacy_parser import LegitimacyParser


class TestLegitimacyParser:
    """Tests for LegitimacyParser.parse()."""

    _AUDIT_SECTION = """\
## Package Legitimacy Audit

| Package | Version | Source | Legitimacy | Notes |
|---------|---------|--------|------------|-------|
| fastapi | 0.115 | PyPI | ✅ Legitimate | Well-known |
| suspicious-pkg | 1.0 | PyPI | ❌ Suspicious | Low downloads |
| unknown-lib | 0.1 | GitHub | ⚠️ Unknown | No provenance |
| typosquat | 2.0 | PyPI | ❌ Suspicious | Typosquat risk |
| uvicorn | 0.32 | PyPI | ✅ Legitimate | Well-known |
"""

    def test_empty_string_returns_empty(self):
        assert LegitimacyParser.parse("") == []

    def test_no_section_returns_empty(self):
        text = "## Research\n\nSome research without a legitimacy audit.\n"
        assert LegitimacyParser.parse(text) == []

    def test_flagged_packages_extracted(self):
        result = LegitimacyParser.parse(self._AUDIT_SECTION)
        assert "suspicious-pkg" in result
        assert "unknown-lib" in result
        assert "typosquat" in result

    def test_legitimate_packages_excluded(self):
        result = LegitimacyParser.parse(self._AUDIT_SECTION)
        assert "fastapi" not in result
        assert "uvicorn" not in result

    def test_count_correct(self):
        result = LegitimacyParser.parse(self._AUDIT_SECTION)
        assert len(result) == 3

    def test_section_bounded_by_next_heading(self):
        """Packages in a different section are not picked up."""
        text = (
            "## Package Legitimacy Audit\n\n"
            "| Package | Legitimacy |\n"
            "|---------|------------|\n"
            "| bad-pkg | ❌ Suspicious |\n\n"
            "## Another Section\n\n"
            "| other-pkg | ❌ Suspicious |\n"
        )
        result = LegitimacyParser.parse(text)
        assert "bad-pkg" in result
        assert "other-pkg" not in result

    def test_case_insensitive_signals(self):
        text = (
            "## Package Legitimacy Audit\n\n"
            "| pkg-a | SUSPICIOUS signal here |\n"
            "| pkg-b | unknown provenance |\n"
        )
        result = LegitimacyParser.parse(text)
        assert "pkg-a" in result
        assert "pkg-b" in result

    def test_all_legitimate_returns_empty(self):
        text = (
            "## Package Legitimacy Audit\n\n"
            "| Package | Legitimacy |\n"
            "|---------|------------|\n"
            "| fastapi | ✅ Legitimate |\n"
            "| uvicorn | ✅ Verified |\n"
        )
        result = LegitimacyParser.parse(text)
        assert result == []
