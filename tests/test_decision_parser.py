"""Unit tests for DecisionParser."""

from __future__ import annotations

import pytest

from gsd_monitor.parsers.decision_parser import DecisionParser


class TestDecisionParser:
    """Tests for DecisionParser.parse()."""

    def test_empty_string_returns_empty(self):
        assert DecisionParser.parse("") == []

    def test_no_decisions_returns_empty(self):
        text = "## Context\n\nSome context with no decisions.\n"
        assert DecisionParser.parse(text) == []

    def test_single_decision_with_colon(self):
        text = "## Decisions\n\n- **D-01:** We chose FastAPI for async support\n"
        result = DecisionParser.parse(text)
        assert len(result) == 1
        assert result[0].id == "D-01"
        assert result[0].text == "We chose FastAPI for async support"
        assert result[0].is_covered is False

    def test_multiple_decisions(self):
        text = (
            "## Decisions\n\n"
            "- **D-01:** FastAPI for async\n"
            "- **D-02:** pywebview over Electron\n"
            "- **D-03:** Tailwind v4 with Vite\n"
        )
        result = DecisionParser.parse(text)
        assert len(result) == 3
        assert result[0].id == "D-01"
        assert result[1].id == "D-02"
        assert result[2].id == "D-03"

    def test_decision_id_zero_padded(self):
        text = "- **D-1:** Single digit id\n"
        result = DecisionParser.parse(text)
        assert len(result) == 1
        assert result[0].id == "D-01"

    def test_is_covered_default_false(self):
        text = "- **D-01:** A decision\n"
        result = DecisionParser.parse(text)
        assert result[0].is_covered is False

    def test_decisions_mixed_with_other_content(self):
        text = (
            "## Context\n\nSome prose.\n\n"
            "## Decisions\n\n"
            "- **D-01:** First decision\n"
            "\nMore prose in between.\n\n"
            "- **D-02:** Second decision\n"
        )
        result = DecisionParser.parse(text)
        assert len(result) == 2

    def test_non_decision_bullets_ignored(self):
        text = (
            "- Some regular bullet\n"
            "- **D-01:** Real decision\n"
            "- **Note:** Not a decision\n"
        )
        result = DecisionParser.parse(text)
        assert len(result) == 1
        assert result[0].id == "D-01"
