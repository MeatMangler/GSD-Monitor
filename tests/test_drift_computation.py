"""Unit tests for _compute_drift helper in project_discovery.py (TDD RED phase)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from gsd_monitor.models.enums import DriftIndicator, PhaseStatus
from gsd_monitor.services.project_discovery import _compute_drift

NOW = datetime(2026, 4, 12, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# No plan cases
# ---------------------------------------------------------------------------


def test_no_plan_not_started_returns_deferred() -> None:
    result = _compute_drift(PhaseStatus.NOT_STARTED, None, None, now=NOW)
    assert result == DriftIndicator.DEFERRED


def test_no_plan_in_progress_returns_deferred() -> None:
    """D-01: IN_PROGRESS with no plan also returns DEFERRED."""
    result = _compute_drift(PhaseStatus.IN_PROGRESS, None, None, now=NOW)
    assert result == DriftIndicator.DEFERRED


def test_no_plan_complete_returns_none() -> None:
    result = _compute_drift(PhaseStatus.COMPLETE, None, None, now=NOW)
    assert result == DriftIndicator.NONE


# ---------------------------------------------------------------------------
# Complete phase cases (D-02: done is done regardless of age)
# ---------------------------------------------------------------------------


def test_complete_with_old_last_updated_returns_none() -> None:
    """D-02: COMPLETE phase with last_updated 60 days old still returns NONE."""
    plan_write_time = NOW - timedelta(days=60)
    last_updated = NOW - timedelta(days=60)
    result = _compute_drift(PhaseStatus.COMPLETE, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.NONE


def test_complete_with_recent_activity_returns_none() -> None:
    plan_write_time = NOW - timedelta(days=5)
    last_updated = NOW - timedelta(days=2)
    result = _compute_drift(PhaseStatus.COMPLETE, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.NONE


# ---------------------------------------------------------------------------
# MAJOR drift: last_updated > 30 days
# ---------------------------------------------------------------------------


def test_has_plan_last_updated_over_30_days_returns_major() -> None:
    plan_write_time = NOW - timedelta(days=45)
    last_updated = NOW - timedelta(days=45)
    result = _compute_drift(PhaseStatus.IN_PROGRESS, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.MAJOR


def test_has_plan_last_updated_exactly_31_days_returns_major() -> None:
    plan_write_time = NOW - timedelta(days=31)
    last_updated = NOW - timedelta(days=31)
    result = _compute_drift(PhaseStatus.IN_PROGRESS, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.MAJOR


# ---------------------------------------------------------------------------
# MINOR drift: last_updated 7-30 days
# ---------------------------------------------------------------------------


def test_has_plan_last_updated_7_to_30_days_returns_minor() -> None:
    plan_write_time = NOW - timedelta(days=20)
    last_updated = NOW - timedelta(days=20)
    result = _compute_drift(PhaseStatus.IN_PROGRESS, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.MINOR


def test_has_plan_last_updated_exactly_7_days_returns_minor() -> None:
    plan_write_time = NOW - timedelta(days=7)
    last_updated = NOW - timedelta(days=7)
    result = _compute_drift(PhaseStatus.IN_PROGRESS, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.MINOR


# ---------------------------------------------------------------------------
# NONE drift: last_updated < 7 days
# ---------------------------------------------------------------------------


def test_has_plan_last_updated_under_7_days_returns_none() -> None:
    plan_write_time = NOW - timedelta(days=3)
    last_updated = NOW - timedelta(days=3)
    result = _compute_drift(PhaseStatus.IN_PROGRESS, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.NONE


# ---------------------------------------------------------------------------
# Fallback to plan_write_time when last_updated is None
# ---------------------------------------------------------------------------


def test_has_plan_no_last_updated_falls_back_to_plan_write_time() -> None:
    """When last_updated is None, fall back to plan_write_time for age calculation."""
    plan_write_time = NOW - timedelta(days=45)
    result = _compute_drift(PhaseStatus.IN_PROGRESS, plan_write_time, None, now=NOW)
    assert result == DriftIndicator.MAJOR


# ---------------------------------------------------------------------------
# NEEDS_VERIFICATION status
# ---------------------------------------------------------------------------


def test_needs_verification_status_computes_normally() -> None:
    """NEEDS_VERIFICATION is not COMPLETE, so drift rules apply normally."""
    plan_write_time = NOW - timedelta(days=10)
    last_updated = NOW - timedelta(days=10)
    result = _compute_drift(PhaseStatus.NEEDS_VERIFICATION, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.MINOR


# ---------------------------------------------------------------------------
# Boundary: exactly 30 days is MINOR, not MAJOR
# ---------------------------------------------------------------------------


def test_exactly_30_days_returns_minor_not_major() -> None:
    """Boundary: age_days == 30 uses >= 7 check (MINOR), not > 30 check (MAJOR)."""
    plan_write_time = NOW - timedelta(days=30)
    last_updated = NOW - timedelta(days=30)
    result = _compute_drift(PhaseStatus.IN_PROGRESS, plan_write_time, last_updated, now=NOW)
    assert result == DriftIndicator.MINOR
