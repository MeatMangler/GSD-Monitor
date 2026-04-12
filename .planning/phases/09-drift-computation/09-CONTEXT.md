# Phase 9: Drift Computation - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the hardcoded `DriftIndicator.DEFERRED` in `_enrich_phase` and `_enrich_gsd2_slice` with real computed values derived from `plan_write_time`, `last_updated`, and `phase.status`. This is a pure backend change — no UI, no new endpoints, no schema changes.

</domain>

<decisions>
## Implementation Decisions

### Edge Cases (gaps in DRFT-01)
- **D-01:** `IN_PROGRESS` phase with no plan → `DriftIndicator.DEFERRED`. Same as `NOT_STARTED + no plan` — no plan means no meaningful work has started, regardless of the status label. Keeps the visual signal consistent.
- **D-02:** `COMPLETE` phase with `last_updated` > 30 days old → `DriftIndicator.NONE`. Done is done — the 30-day age threshold only applies to active/in-progress phases. A completed phase never drifts.

### Code Structure
- **D-03:** Extract a shared private helper `_compute_drift(status, plan_write_time, last_updated, now)` — called from both `_enrich_phase` and `_enrich_gsd2_slice`. No duplicated logic. Lives as a module-level or class-level helper in `project_discovery.py`.
- **D-04:** `now` is injectable via a default parameter: `_compute_drift(..., now: datetime | None = None)` — defaults to `datetime.now(tz=timezone.utc)` when `None`. Tests pass a fixed `datetime` to control time without needing freezegun.

### GSD-2 Data Gap
- **D-05:** `_enrich_gsd2_slice` should fall back to `plan_file.stat().st_mtime` for `last_updated` when no `summary.md` exists — matching GSD-1 behavior. This ensures drift computation is consistent across both GSD versions.

### Claude's Discretion
- Exact placement of `_compute_drift` (module-level function vs. private static on the service class) — follow existing codebase conventions.
- Whether to add tests to the existing test files or a new `test_drift_computation.py`.

</decisions>

<drift_logic>
## Drift Logic Reference

Derived from DRFT-01 requirements + decisions above:

```
def _compute_drift(status, plan_write_time, last_updated, now=None):
    now = now or datetime.now(tz=timezone.utc)

    # No plan at all
    if plan_write_time is None:
        if status == PhaseStatus.COMPLETE:
            return DriftIndicator.NONE  # done without a formal plan — fine
        return DriftIndicator.DEFERRED  # NOT_STARTED or IN_PROGRESS, no plan

    # Phase is complete — never drifts regardless of age
    if status == PhaseStatus.COMPLETE:
        return DriftIndicator.NONE

    # Has a plan; compute age
    age_days = (now - last_updated).days if last_updated else (now - plan_write_time).days

    if age_days > 30:
        return DriftIndicator.MAJOR
    if age_days >= 7:
        return DriftIndicator.MINOR
    return DriftIndicator.NONE
```

Success criteria cross-check:
1. No plan + NOT_STARTED → DEFERRED ✓
2. Plan + last_updated > 30 days → MAJOR ✓
3. Plan + last_updated 7–30 days → MINOR ✓
4. COMPLETE + recent activity → NONE ✓
5. (D-01) IN_PROGRESS + no plan → DEFERRED ✓
6. (D-02) COMPLETE + old last_updated → NONE ✓

</drift_logic>

<canonical_refs>
## Canonical References

- `.planning/REQUIREMENTS.md` — DRFT-01 (full drift logic spec)
- `gsd_monitor/services/project_discovery.py` — `_enrich_phase` (lines ~330–430), `_enrich_gsd2_slice` (lines ~575–655)
- `gsd_monitor/models/enums.py` — `DriftIndicator`, `PhaseStatus`

</canonical_refs>
