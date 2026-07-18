"""Unit tests for ReviewParser."""

from __future__ import annotations

import pytest

from gsd_monitor.parsers.review_parser import ReviewParser
from gsd_monitor.models.core import ReviewSummary


class TestReviewParser:
    """Tests for ReviewParser.parse()."""

    def test_empty_string_returns_none(self):
        assert ReviewParser.parse("") is None

    def test_table_format_all_severities(self):
        text = (
            "# Review\n\n"
            "| Severity | Count |\n"
            "|----------|-------|\n"
            "| Critical | 2 |\n"
            "| Warning | 3 |\n"
            "| Info | 1 |\n"
        )
        result = ReviewParser.parse(text)
        assert result is not None
        assert result.critical == 2
        assert result.warning == 3
        assert result.info == 1

    def test_table_format_partial(self):
        text = (
            "| Critical | 1 |\n"
            "| Warning | 0 |\n"
        )
        result = ReviewParser.parse(text)
        assert result is not None
        assert result.critical == 1
        assert result.warning == 0
        assert result.info == 0

    def test_heading_format_counts_bullets(self):
        text = (
            "## Critical\n\n"
            "- Issue one\n"
            "- Issue two\n\n"
            "## Warning\n\n"
            "- Warning issue\n\n"
            "## Info\n\n"
            "- Info note\n"
            "- Info note 2\n"
        )
        result = ReviewParser.parse(text)
        assert result is not None
        assert result.critical == 2
        assert result.warning == 1
        assert result.info == 2

    def test_heading_findings_suffix(self):
        """'## Critical Findings' is also recognized."""
        text = (
            "## Critical Findings\n\n"
            "- One critical\n"
        )
        result = ReviewParser.parse(text)
        assert result is not None
        assert result.critical == 1

    def test_no_severities_returns_zero_summary(self):
        """File with no severity markers returns ReviewSummary(0, 0, 0) not None."""
        text = "# Code Review\n\nLooks good overall.\n"
        result = ReviewParser.parse(text)
        assert result is not None
        assert result.critical == 0
        assert result.warning == 0
        assert result.info == 0

    def test_case_insensitive(self):
        text = "| CRITICAL | 5 |\n| WARNING | 2 |\n"
        result = ReviewParser.parse(text)
        assert result is not None
        assert result.critical == 5
        assert result.warning == 2
