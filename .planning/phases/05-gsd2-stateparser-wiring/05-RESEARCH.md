# Phase 5: GSD-2 StateParser Wiring - Research

**Researched:** 2026-04-04
**Domain:** Python backend — `ProjectDiscoveryService._discover_gsd2()`, `StateParser`
**Confidence:** HIGH

## Summary

Phase 5 is a minimal, surgical wiring change. `StateParser` is already written, imported, and fully functional. `_build_gsd1_segment()` (GSD-1 path) already calls it correctly — Phase 4 wired that half. `_discover_gsd2()` (GSD-2 path) reads `state.md` only for mtime and never passes it through `StateParser`, so `state_current_position` is always `None` on GSD-2 segments.

The fix is ~12 lines added to `_discover_gsd2()` just before the final `SegmentModel(...)` constructor call, following the exact pattern already established in `_build_gsd1_segment()` — but with GSD-2-appropriate field priority (`active_slice` before `status`). No new imports, no model changes, no API changes, no frontend changes are required. The TypeScript interface already declares `stateCurrentPosition?: string | null` and `DashboardPage.tsx` already consumes it with the correct null-safe fallback chain.

This phase closes the partial gap in PERF-03 identified in the v1.0 audit. The total implementation surface is one Python file, one method, one block of code.

**Primary recommendation:** Add a StateParser call block to `_discover_gsd2()` in `gsd_monitor/services/project_discovery.py`, mirroring `_build_gsd1_segment()` but with GSD-2 field priority order.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PERF-03 (GSD-2) | `StateParser` wired into discovery pipeline — active phase, active milestone, and workflow position populated on GSD-2 segments | `_discover_gsd2()` already imports `StateParser` (line 24) and reads `state.md` for mtime. Pattern is fully established in `_build_gsd1_segment()`. Only the StateParser call + `state_current_position` field assignment is missing. |
</phase_requirements>

## Standard Stack

No new libraries needed. All components already exist in the project.

### Core (already present)
| Component | Location | Purpose |
|-----------|----------|---------|
| `StateParser` | `gsd_monitor/parsers/state_parser.py` | Parses `state.md` / `STATE.md` into `StateInfo` |
| `StateInfo` | `gsd_monitor/models/core.py` | Model with `status`, `active_slice`, `active_milestone`, `active_task`, `workflow_phase` |
| `_discover_gsd2()` | `gsd_monitor/services/project_discovery.py:469` | GSD-2 discovery method — change target |
| `SegmentModel.state_current_position` | `project_discovery.py:83` | Already defined as `str | None = None` |

**No installation needed.** Zero new dependencies.

## Architecture Patterns

### How GSD-1 Does It (the authoritative pattern, Phase 4 decision)

From `_build_gsd1_segment()` lines 243-255:

```python
# PERF-03: Wire StateParser for active phase position
state_position: str | None = None
for state_name in ("STATE.md", "state.md"):
    state_path = base / state_name
    if state_path.is_file():
        state_result = StateParser.parse(str(state_path))
        if state_result.is_success and state_result.value:
            si = state_result.value
            # GSD-1: prefer status text; GSD-2: prefer active_slice
            pos = si.status or si.active_slice or ""
            if pos.strip():
                state_position = pos.strip()
        break  # Only try the first existing file

sm = SegmentModel(
    ...
    state_current_position=state_position,
)
```

### GSD-2 Adaptation

GSD-2 `state.md` files use the `# GSD State` format with `**Active Slice:**` fields (parsed by `StateParser` into `StateInfo.active_slice`). The comment in the existing GSD-1 code already anticipates this: `"GSD-1: prefer status text; GSD-2: prefer active_slice"`. For GSD-2, the field priority should be: `active_slice → status → ""`.

The GSD-2 state file path is `gsd_dir / "state.md"` (lowercase, confirmed at line 526). There is no uppercase variant to try in GSD-2 — only one filename to check. The mtime-reading block at lines 526-532 proves the path exists and is correct.

### Change Location in `_discover_gsd2()`

The `SegmentModel(...)` construction is at lines 534-542 and returns with `state_current_position` left at default `None`. The StateParser call block must be inserted between the `_enrich_gsd2_project(...)` call (line 533) and the `return SegmentModel(...)` (line 534).

```python
# PERF-03 (GSD-2): Wire StateParser for active phase position
state_position: str | None = None
state_path = gsd_dir / "state.md"
if state_path.is_file():
    state_result = StateParser.parse(str(state_path))
    if state_result.is_success and state_result.value:
        si = state_result.value
        # GSD-2: prefer active_slice; fall back to status text
        pos = si.active_slice or si.status or ""
        if pos.strip():
            state_position = pos.strip()

return SegmentModel(
    segment_key="gsd2",
    gsd_project=None,
    workstream=None,
    gsd_version=GsdVersion.V2,
    planning_path=str(gsd_dir),
    repo_root=str(repo_dir),
    project=proj,
    state_current_position=state_position,   # was missing
)
```

### Exception Safety

`_discover_gsd2()` already has a broad `except Exception` at line 543 that catches all failures and returns a fallback `SegmentModel`. The StateParser call is inside the `try` block, so any failure is safe. `StateParser.parse()` itself also catches all exceptions internally (line 43 of `state_parser.py`).

### Anti-Patterns to Avoid

- **Duplicating the mtime loop:** The mtime block (lines 526-532) already walks `state.md`. Do not merge the StateParser call into the mtime block — keep them separate for clarity and correctness.
- **Adding uppercase fallback for GSD-2:** GSD-2 convention is lowercase `state.md` in `.gsd/`. Don't copy the GSD-1 two-name loop — single path check is correct.
- **Touching the fallback SegmentModel at line 544:** The `except` branch returns a bare SegmentModel with no position — this is correct; don't add StateParser calls to the error path.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Parsing state.md | Custom regex | `StateParser.parse()` — already handles both GSD-1 and GSD-2 formats, error handling included |
| Accessing StateInfo fields | Direct dict access | `state_result.value` is a typed `StateInfo` Pydantic model |

## Common Pitfalls

### Pitfall 1: Inserting After the Return
**What goes wrong:** StateParser call placed after the `return SegmentModel(...)` line — dead code, field stays `None`.
**Why it happens:** `_discover_gsd2()` is a long method and the return is easy to miss.
**How to avoid:** Insert the block between line 533 (`proj = self._enrich_gsd2_project(...)`) and line 534 (`return SegmentModel(...)`), then update the `return` to pass `state_current_position=state_position`.
**Warning signs:** Tests pass structurally but `state_current_position` is always `None` in API output for GSD-2 projects.

### Pitfall 2: Wrong Field Priority for GSD-2
**What goes wrong:** Using `si.status or si.active_slice` (GSD-1 order) instead of `si.active_slice or si.status` (GSD-2 order).
**Why it happens:** Directly copying GSD-1 code without adapting for GSD-2 format.
**How to avoid:** GSD-2 state.md uses `# GSD State` heading with `**Active Slice:**` — `StateParser` populates `active_slice` for this format. GSD-1 uses `## Current Position` prose — `StateParser` populates `status`. Use GSD-2 priority: `active_slice → status`.

### Pitfall 3: Forgetting to Pass the Field in SegmentModel Constructor
**What goes wrong:** StateParser is called, `state_position` is computed correctly, but `state_current_position=state_position` is not added to the `return SegmentModel(...)` kwargs.
**Why it happens:** `SegmentModel` defaults `state_current_position=None` so Python won't error; the bug is silent.
**How to avoid:** Verify the return statement at line 534 includes `state_current_position=state_position` after the change.

## Code Examples

### StateParser Behavior — GSD-2 Format
```python
# Source: gsd_monitor/parsers/state_parser.py lines 27-38
# For files containing "# GSD State":
StateInfo(
    active_milestone="M1",   # from **Active Milestone:**
    active_slice="S3",        # from **Active Slice:** — use this for GSD-2
    active_task="T2",         # from **Active Task:**
    workflow_phase="plan",    # from **Phase:**
    status="",                # empty for GSD State format
)

# Source: gsd_monitor/parsers/state_parser.py lines 40-58
# For files WITHOUT "# GSD State" (GSD-1 style):
StateInfo(
    status="Phase: 04\nPlan: Not started",  # from ## Current Position section
    active_milestone=None,
    active_slice=None,
)
```

### StateInfo Model
```python
# Source: gsd_monitor/models/core.py lines 93-100
class StateInfo(BaseModel):
    current_phase: str = ""
    status: str = ""            # GSD-1 path: _extract_current_position_text()
    last_activity: datetime | None = None
    active_milestone: str | None = None
    active_slice: str | None = None    # GSD-2 path: **Active Slice:** match
    active_task: str | None = None
    workflow_phase: str | None = None
```

### Frontend Consumption (no changes needed)
```typescript
// Source: frontend/src/pages/DashboardPage.tsx lines 61-64
const activePhaseName =
  activeSegment?.stateCurrentPosition ??       // populated by this phase
  phases.find((p) => p.status === "in_progress")?.title ??
  "—";

// Source: frontend/src/api.ts line 93
stateCurrentPosition?: string | null;          // already typed correctly
```

## Environment Availability

Step 2.6: SKIPPED (no external dependencies — Python-only backend change, no new tools, services, CLIs, or runtimes required).

## Validation Architecture

Nyquist validation is disabled (`workflow.nyquist_validation: false` in `.planning/config.json`). Skipping this section.

The existing test suite uses `pytest` with `httpx`/`TestClient`. A unit test for `_discover_gsd2()` with a tmp_path fixture that creates a minimal `.gsd/state.md` would verify PERF-03.

## Sources

### Primary (HIGH confidence)
- `gsd_monitor/services/project_discovery.py` — direct code inspection of `_discover_gsd2()` (lines 469-552) and `_build_gsd1_segment()` (lines 222-268)
- `gsd_monitor/parsers/state_parser.py` — direct code inspection of `StateParser.parse()` and `StateInfo` field mapping
- `gsd_monitor/models/core.py` — `StateInfo`, `SegmentModel` field definitions
- `frontend/src/api.ts` line 93 — `stateCurrentPosition?: string | null` already in TypeScript interface
- `frontend/src/pages/DashboardPage.tsx` lines 61-64, 79-83 — null-safe consumption of `stateCurrentPosition`

### Secondary (MEDIUM confidence)
- `.planning/STATE.md` decisions log (line 87): `"[Phase 04-02]: StateParser called in _build_gsd1_segment; STATE.md position text is authoritative source for active phase display on dashboard"` — confirms design intent

## Metadata

**Confidence breakdown:**
- Change target: HIGH — code read directly; exact insertion point identified
- Implementation pattern: HIGH — direct copy of Phase 4 GSD-1 precedent with GSD-2 field order adaptation
- Frontend impact: HIGH — no changes needed; already consuming `stateCurrentPosition` with correct null fallback
- Test coverage: MEDIUM — existing test suite has no test for `_discover_gsd2()` specifically; a new unit test should be added

**Research date:** 2026-04-04
**Valid until:** 2026-05-04 (stable codebase, no external dependencies)
