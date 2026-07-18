# GSD Monitor: Full Visibility for gsd-core Projects

> Status: Approved for implementation — routed to v4.0 milestone (Phases 14–16)
> Source of truth: [gsd-core User Guide](https://opengsd.net/docs/v1/user-guide)
> Scope: Read-only. Every change preserves existing GSD-1 behavior via fallback-based detection.

## Purpose

GSD Monitor's primary job is to give **full visibility into all GSD workflow documentation** created while developing projects. This review compares the gsd-core (opengsd v1) file/workflow model against what the monitor currently discovers, parses, and renders.

The monitor was built around an older `.planning/` shape and this app's own PRD. As a result, several gsd-core artifacts are **silently invisible**, and a few are **outright mis-parsed**. Work is grouped:

- **P0** — correctness bugs that make gsd-core artifacts invisible today
- **P1** — surface high-value gsd-core artifacts
- **P2** — new artifact views + lifecycle signals

---

## Reference: what gsd-core writes vs. what the monitor reads

gsd-core per-phase files (from the walkthrough + Project File Structure):

- `XX-YY-PLAN.md` (XML `<task>` blocks), `XX-YY-SUMMARY.md`
- `CONTEXT.md`, `RESEARCH.md`, `VERIFICATION.md`, `UAT.md` — **no number prefix**
- `XX-UI-SPEC.md`, `XX-UI-REVIEW.md`, `XX-VALIDATION.md`, `XX-REVIEW.md` — prefixed

Top-level dirs: `spikes/`, `sketches/`, `seeds/`, `threads/`, `debug/` (+ `resolved/`), `reports/`, `todos/pending|done/`, `codebase/`, `intel/`, `research/`, plus backlog phases numbered `999.x`.

---

## P0 — Correctness bugs that hide gsd-core artifacts (highest impact)

### 1. Unprefixed phase artifacts read as absent

`gsd_monitor/services/project_discovery.py` `_enrich_phase` only checks padded names:

```512:516:gsd_monitor/services/project_discovery.py
            ctx_file = phase_dir / f"{padded}-CONTEXT.md"
            research_file = phase_dir / f"{padded}-RESEARCH.md"
            uat_file = phase_dir / f"{padded}-UAT.md"
            ui_spec_file = phase_dir / f"{padded}-UI-SPEC.md"
            ui_review_file = phase_dir / f"{padded}-UI-REVIEW.md"
```

gsd-core writes `CONTEXT.md`, `RESEARCH.md`, `VERIFICATION.md`, `UAT.md` with **no prefix**, so `has_context` / `has_research` / `has_uat` / `has_validation`, `research_content`, and `validation_content` are all false/empty for gsd-core projects. The `VerificationPage` and research/validation drawers are effectively blank.

Note: `has_validation` already tries both `-VALIDATION.md` AND `-VERIFICATION.md` variants (line 522), but both are still prefixed — bare `VERIFICATION.md` is still missed.

- **Fix:** resolve each artifact by trying `{padded}-NAME.md` first, then bare `NAME.md` (helper `_resolve_artifact(phase_dir, padded, "CONTEXT")`). Apply to CONTEXT, RESEARCH, VERIFICATION, UAT (VALIDATION / UI-SPEC / UI-REVIEW stay prefixed but the helper handles both harmlessly).
- **Tests:** add fixtures with unprefixed names in `tests/test_discovery_gsd_core.py` (currently only `01-UI-SPEC.md`, `01-01-PLAN.md`, etc. are covered — CONTEXT/RESEARCH/VERIFICATION/UAT are never tested).

### 2. Phase-dir enrichment collision for milestone-prefixed codes ← NEW BUG

`_enrich_phase` computes `padded = f"{phase.number:02d}"`. For gsd-core phases, `_parse_phase_id("1-01")` returns `(1, "1-01")`, so `phase.number = 1` for every phase in milestone 1.

The directory scan (`d.name.lower().startswith(padded + "-")`) then matches `01-01-*`, `01-02-*`, and `01-03-*` **all to the same first hit**. Every phase within the same milestone gets enriched from an arbitrary single directory — silent data collision.

- **Fix:** when `phase.code` contains a `-`, reconstruct the full zero-padded prefix. `code "1-01"` → dir prefix `"01-01-"`. Replace the single `padded` lookup with a `_phase_dir_prefix(phase)` helper that handles both the simple case (GSD-1: `"01-"`) and the milestone-prefixed case (gsd-core: `"01-01-"`).
- **Impact:** without this fix, every multi-phase gsd-core milestone shows the same plan/todos/artifacts for all its phases.

### 3. PLAN.md XML tasks not parsed

`gsd_monitor/parsers/plan_parser.py` only extracts `- [ ]` lines. gsd-core plans are XML:

```
<task type="auto">
  <name>Create validateSignature core function</name>
  <files>src/validate.js</files>
  <verify>npm test</verify>
  <done>All timing-safe tests pass</done>
</task>
```

Result: `todos` is empty for every gsd-core plan; the Dashboard phase drawer shows no tasks.

- **Fix:** extend `PlanParser` to also parse `<task ...>...</task>` blocks (name, files, verify, done, `type`), keeping the checkbox path as fallback. Surface task `type` so `checkpoint:human-verify` (package-verification gates) is visible.

### 4. REQUIREMENTS.md parser hardcoded to this app's own PRD

`gsd_monitor/parsers/requirements_parser.py` bounds parsing to `## v3.0 Requirements`:

```34:34:gsd_monitor/parsers/requirements_parser.py
_V3_SECTION = re.compile(r"^##\s+v3\.0\s+Requirements\s*$", re.MULTILINE | re.IGNORECASE)
```

There is a fallback (lines 93–96) that scans the whole file when no `## v3.0 Requirements` section is found — so gsd-core files are scanned. However the `_REQ_LINE` regex requires checkbox syntax (`- [x] **REQ-001**: description`) which may not match gsd-core format. Additionally `RequirementsParser` is not exported from `gsd_monitor/parsers/__init__.py` and its call site in `project_discovery.py` should be verified.

- **Fix:** verify `RequirementsParser` is wired into the discovery pipeline; make the ID regex generic; export from `__init__.py`. If gsd-core uses a different requirement format, add a second parse path.

### 5. Reserved-dir set misclassifies gsd-core folders as sub-projects

`gsd_monitor/services/planning_layout.py` `RESERVED` omits `spikes`, `sketches`, `reports`, `todos`, `debug`, `intel`. In multi-project layouts these can be walked as fake "projects" if they happen to contain `ROADMAP.md`, `STATE.md`, or a `phases/` dir.

- **Fix:** add the missing gsd-core reserved names.

---

## P1 — Surface high-value gsd-core artifacts

### 6. CONTEXT.md decisions + coverage status

Decisions (`- **D-01:** ...`) are a flagship gsd-core concept with a blocking plan-gate and verify-gate warnings written into `VERIFICATION.md`. Today only `has_context` (a bool) exists.

- Add a `DecisionParser` for the decisions block; add `decisions: list[Decision]` to `PhaseEntry` in `gsd_monitor/models/core.py`; show them in the Dashboard phase drawer with a covered/uncovered indicator (parse the decision-coverage warning section from VERIFICATION.md).

### 7. Code review findings (`XX-REVIEW.md`)

`/gsd-code-review` writes Critical/Warning/Info findings — a core quality gate the monitor ignores entirely (no flag, no parser).

- Add `has_review` + a lightweight severity-count parse; show a badge on phases and a section in `VerificationPage`.

### 8. RESEARCH.md Package Legitimacy Audit (security)

gsd-core RESEARCH.md includes a `## Package Legitimacy Audit` table with `[OK]` / `[SUS]` / `[SLOP]` verdicts and "Packages removed/flagged" lines.

- Parse and surface flagged/removed packages as a security signal on the phase (high-visibility, safety-relevant).

---

## P2 — New artifact views + lifecycle signals

### 9. VerificationPage: structured render for gsd-core VERIFICATION.md

Currently renders raw markdown. gsd-core VERIFICATION.md has structured sections: verification result, decision coverage warnings, open blockers. A structured parse would let the page highlight **open blockers vs passing gates** rather than a wall of text.

### 10. Top-level artifact explorers

Add read-only views (or a unified "Artifacts" page with sections) for the gsd-core dirs currently only reachable via the Docs file tree:

- **Spikes:** `.planning/spikes/MANIFEST.md` + `NNN-*/README.md` verdicts (VALIDATED / INVALIDATED / PARTIAL)
- **Sketches:** `.planning/sketches/MANIFEST.md` + open `index.html` externally (reuse existing `POST /api/docs/.../open`)
- **Seeds:** `.planning/seeds/SEED-NNN-*.md`
- **Threads:** `.planning/threads/*.md` (Goal / Context / Next Steps)
- **Debug:** `.planning/debug/` + `resolved/`
- **Reports:** `.planning/reports/`
- **Codebase/Intel:** `.planning/codebase/{STACK,ARCHITECTURE,CONVENTIONS,CONCERNS}.md`, `.planning/intel/`

These are additive endpoints modeled on the existing `/api/quick-tasks/{path}` and `/api/insights/{path}` handlers in `gsd_monitor/api/app.py`.

### 11. Backlog phases (999.x)

Two-level fix needed:
1. `gsd_core_roadmap.py` `_HEADING_PHASE` regex (`[\d]+(?:-[\d]+)?`) matches `999-1` but **not** `999.1` (dot separator). Backlog phases never appear in the roadmap parse.
2. `_enrich_phase` matches dirs by `f"{phase.number:02d}"`, so `999.x-...` never enriches even if parsed.

Support the `999.x` numbering in the roadmap parser + phase-dir match, or add a dedicated backlog list.

### 12. Richer config + lifecycle signals

- Surface more of `config.json` on the Dashboard: `workflow.nyquist_validation`, `workflow.ui_phase`, `workflow.discuss_mode`, the `models` block, `dynamic_routing`, `plan_review.source_grounding` (currently only workflow_mode / model_profile / branching_strategy badges show). `nyquist_validation` flag is particularly important — it changes what VerificationPage should display.
- Surface `PROJECT.md` vision prominently (project description/vision), not just via the file tree. Even a single "Vision:" callout on the Dashboard summary card would materially improve orientation.
- **Ship/PR status:** use the existing `GitService` to show shipped phases / recent phase commits (`feat(01-01): ...`) and, if available, PR links, so "verified vs shipped" is visible.

---

## Implementation plan

Routed to **v4.0 — gsd-core Full Visibility** (Phases 14–16). Phase 13 (installer) deferred to v5.0.

### Phase 14: P0 Correctness Bug Fixes
- Plan 14-01: Unprefixed artifact fallback (`_resolve_artifact` helper) + VERIFICATION bare detection
- Plan 14-02: Phase-dir enrichment collision fix (`_phase_dir_prefix` helper for milestone-prefixed codes)
- Plan 14-03: XML task parsing in `PlanParser` + `RequirementsParser` wiring verification + reserved dir hardening

### Phase 15: P1 Artifact Visibility
- Plan 15-01: `DecisionParser` + `PhaseEntry.decisions` + Dashboard drawer integration
- Plan 15-02: `ReviewParser` (XX-REVIEW.md severity counts) + phase badge + VerificationPage section
- Plan 15-03: Package legitimacy audit parser (RESEARCH.md) + security signal per phase

### Phase 16: P2 Surface Depth
- Plan 16-01: Backlog phases (999.x) — roadmap regex + enrichment fix
- Plan 16-02: Config signal expansion (nyquist_validation, discuss_mode, ui_phase) + PROJECT.md vision on Dashboard
- Plan 16-03: VerificationPage structured render for gsd-core VERIFICATION.md
- Plan 16-04: Top-level artifact explorers (Spikes, Threads, Codebase/Intel) — new API endpoints + frontend views

---

## Suggested sequencing

P0 first (correctness), then P1 (high-value parsers), then P2 breadth. All changes stay read-only and preserve GSD-1 behavior via fallback-based detection.

## Verification approach

- Unit tests per parser (XML plan tasks, generic requirements, decisions, review, package audit).
- Discovery tests with both prefixed and unprefixed phase artifacts.
- Discovery tests with milestone-prefixed codes (1-01, 1-02, 2-01) confirming no enrichment collision.
- Point a scan root at a real gsd-core project and confirm CONTEXT / RESEARCH / VERIFICATION / UAT, tasks, decisions, and requirements all populate.

---

## Appendix: impact summary

| Area | Today (gsd-core project) | After |
| --- | --- | --- |
| CONTEXT / RESEARCH / VERIFICATION / UAT | Invisible (wrong filename lookup) | Detected + rendered |
| Phase enrichment (multi-phase milestones) | Collision — all phases show same data | Correct per-phase directory matching |
| Plan tasks | Empty (XML not parsed) | Task list with verify/done/type |
| Requirements | Possibly dropped (format mismatch; wiring unverified) | Parsed + phase-linked |
| Decisions (D-01..) | Not surfaced | Shown with coverage status |
| Code review findings | Not surfaced | Severity badges + section |
| Package legitimacy audit | Not surfaced | Security signal per phase |
| Backlog (999.x) | Invisible (regex + enrichment both broken) | Enriched / listed |
| Config signals | 3 badges (workflow_mode, model_profile, branching) | Full config visibility incl. nyquist_validation |
| PROJECT.md vision | File-tree only | Prominent Dashboard callout |
| Spikes / sketches / seeds / threads / debug / reports | File-tree only | Dedicated views |
