"""Discover GSD projects — GSD-1 (checkbox format) and gsd-core (heading-based format)."""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

from gsd_monitor.models.core import GsdProject, Milestone, PhaseEntry, TodoItem
from gsd_monitor.models.enums import (
    DriftIndicator,
    GsdVersion,
    MilestoneStatus,
    PhaseStatus,
    ResearchCoverage,
)
from gsd_monitor.parsers.gsd_core_roadmap import GsdCoreRoadmapParser
from gsd_monitor.parsers.plan_parser import PlanParser
from gsd_monitor.parsers.roadmap import RoadmapParser
from gsd_monitor.parsers.state_parser import StateParser
from gsd_monitor.services.git_service import GitService
from gsd_monitor.services.planning_layout import PlanningContext, iter_planning_contexts, is_workspace_root

_FRONTMATTER = re.compile(r"^---\s*\n.*?^---\s*\n", re.DOTALL | re.MULTILINE)
_NYQUIST = re.compile(r"nyquist_compliant:\s*(true|false)", re.IGNORECASE)
_VERIFICATION = re.compile(r"verification_result:\s*(pass|fail)", re.IGNORECASE)
_EXCLUDED_DIRS: set[str] = {"node_modules", ".venv", ".git", "build", "dist"}

# Pattern to sniff heading-based ROADMAP format (fallback when no config.json)
_HEADING_PHASE_SNIFF = re.compile(r"^#{2,3} Phase \d", re.MULTILINE)


def _try_read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _strip_frontmatter(raw: str) -> str:
    m = _FRONTMATTER.match(raw)
    if m:
        return raw[m.end() :].lstrip()
    return raw


def _try_read_json(path: Path) -> dict | None:
    """Read and parse a JSON file. Returns None on any error (missing, invalid JSON)."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(text)
        if not isinstance(data, dict):
            return None
        return data
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def _resolve_artifact(phase_dir: Path, padded: str, name: str) -> Path:
    """Resolve a phase artifact file: try prefixed form first, fall back to bare name.

    Args:
        phase_dir: The phase directory (e.g. .planning/phases/03-doc-browser/).
        padded:    Zero-padded phase number string (e.g. "03").
        name:      Bare filename without prefix (e.g. "CONTEXT.md").

    Returns:
        Path to the prefixed file if it exists, otherwise Path to the bare file.
        The returned path may not exist — callers must check `.is_file()`.
    """
    prefixed = phase_dir / f"{padded}-{name}"
    if prefixed.is_file():
        return prefixed
    return phase_dir / name


def _compute_drift(
    status: PhaseStatus,
    plan_write_time: datetime | None,
    last_updated: datetime | None,
    now: datetime | None = None,
) -> DriftIndicator:
    """Compute drift indicator from phase status, plan age, and last activity.

    Args:
        status: Current phase status.
        plan_write_time: Timestamp of the most recent plan file (st_mtime).
        last_updated: Timestamp of latest activity (summary mtime, or plan mtime fallback).
        now: Current time; injectable for testing (D-04). Defaults to UTC now.
    """
    now = now or datetime.now(tz=timezone.utc)

    # No plan at all → DEFERRED (D-01: includes IN_PROGRESS with no plan)
    if plan_write_time is None:
        if status == PhaseStatus.COMPLETE:
            return DriftIndicator.NONE  # done without a formal plan
        return DriftIndicator.DEFERRED

    # Phase is complete → never drifts regardless of age (D-02)
    if status == PhaseStatus.COMPLETE:
        return DriftIndicator.NONE

    # Has a plan; compute age from last_updated, falling back to plan_write_time
    age_days = (now - last_updated).days if last_updated else (now - plan_write_time).days

    if age_days > 30:
        return DriftIndicator.MAJOR
    if age_days >= 7:
        return DriftIndicator.MINOR
    return DriftIndicator.NONE


def _resolve_canonical_root(repo_dir: Path) -> Path:
    """Return canonical repo root. For linked worktrees, resolves .git file pointer."""
    dot_git = repo_dir / ".git"
    if dot_git.is_dir():
        return repo_dir
    if dot_git.is_file():
        try:
            content = dot_git.read_text(encoding="utf-8", errors="replace").strip()
            if content.startswith("gitdir:"):
                gitdir_str = content[len("gitdir:"):].strip()
                gitdir_path = Path(gitdir_str)
                if not gitdir_path.is_absolute():
                    gitdir_path = (repo_dir / gitdir_path).resolve()
                else:
                    gitdir_path = gitdir_path.resolve()
                # Structure: <canonical>/.git/worktrees/<name>
                canonical = gitdir_path.parent.parent.parent
                if canonical.is_dir():
                    return canonical
        except OSError:
            pass
    return repo_dir


@dataclass
class SegmentModel:
    segment_key: str
    gsd_project: str | None
    workstream: str | None
    gsd_version: GsdVersion
    planning_path: str
    repo_root: str
    project: GsdProject
    group_id: str = ""
    is_workspace: bool = False
    state_current_position: str | None = None


@dataclass
class WorktreeInfo:
    path: str
    branch: str
    is_primary: bool


@dataclass
class ProjectGroup:
    id: str
    root_path: str
    display_name: str
    is_workspace: bool
    default_segment_key: str | None
    active_workstream_hint: str | None
    segments: list[SegmentModel] = field(default_factory=list)
    worktrees: list[WorktreeInfo] = field(default_factory=list)


class ProjectDiscoveryService:
    def __init__(self, git: GitService | None = None) -> None:
        self._git = git or GitService()

    def discover_groups(self, scan_roots: list[str]) -> list[ProjectGroup]:
        roots = [r for r in scan_roots if r and Path(r).is_dir()]
        skipped = [r for r in scan_roots if r and not Path(r).is_dir()]
        logger.info("[discover] starting scan — %d root(s), %d skipped (not a dir)", len(roots), len(skipped))
        if skipped:
            for s in skipped:
                logger.warning("[discover] scan root does not exist or is not a dir: %s", s)
        by_repo: dict[str, list[SegmentModel]] = {}
        by_repo_worktrees: dict[str, list[tuple[Path, bool]]] = {}

        for root in roots:
            root_path = Path(root).resolve()
            logger.debug("[discover] scanning root: %s", root_path)
            try:
                for planning_dir in self._find_dirs(root_path, ".planning"):
                    if planning_dir.name != ".planning":
                        continue
                    repo_dir = planning_dir.parent
                    canonical = _resolve_canonical_root(repo_dir)
                    canon_key = str(canonical)
                    # Accumulate worktree info regardless of segment deduplication
                    is_primary = (repo_dir / ".git").is_dir()
                    wt_list = by_repo_worktrees.setdefault(canon_key, [])
                    if not any(str(p) == str(repo_dir) for p, _ in wt_list):
                        wt_list.append((repo_dir, is_primary))
                    # Only add segments from the first worktree discovered for this canonical root
                    if canon_key in by_repo:
                        logger.debug("[discover] skipping duplicate canonical root: %s (already from %s)", repo_dir, canon_key)
                        continue
                    hint_t = _try_read(repo_dir / ".planning" / "active-workstream")
                    hint = hint_t.strip() if hint_t else None
                    ws = is_workspace_root(repo_dir)
                    segs_before = sum(len(v) for v in by_repo.values())
                    for ctx in iter_planning_contexts(planning_dir, repo_dir):
                        seg = self._build_gsd1_segment(ctx, ws, hint)
                        if seg:
                            by_repo.setdefault(canon_key, []).append(seg)
                    segs_after = sum(len(v) for v in by_repo.values())
                    logger.debug(
                        "[discover] found planning dir %s — added %d segment(s)",
                        planning_dir, segs_after - segs_before,
                    )
            except PermissionError:
                logger.warning("[discover] PermissionError scanning root: %s", root)
                continue

        logger.info("[discover] scan complete — %d unique repo(s) with segments", len(by_repo))

        groups: list[ProjectGroup] = []
        for repo_key, segments in by_repo.items():
            if not segments:
                continue
            rp = Path(repo_key)
            gid = str(uuid.uuid5(uuid.NAMESPACE_URL, repo_key))
            default_key = None
            hint = None
            t = _try_read(rp / ".planning" / "active-workstream")
            if t:
                hint = t.strip()
            for s in segments:
                s.group_id = gid
                if hint and s.workstream == hint:
                    default_key = s.segment_key
            if default_key is None and segments:
                default_key = segments[0].segment_key
            ws_flag = any(s.is_workspace for s in segments)
            wt_tuples = by_repo_worktrees.get(repo_key, [(rp, True)])
            worktrees = sorted(
                [
                    WorktreeInfo(
                        path=str(wt_path),
                        branch=self._git.get_branch_name(str(wt_path)),
                        is_primary=wt_is_primary,
                    )
                    for wt_path, wt_is_primary in wt_tuples
                ],
                key=lambda wt: (not wt.is_primary, wt.path),
            )
            groups.append(
                ProjectGroup(
                    id=gid,
                    root_path=str(rp),
                    display_name=rp.name,
                    is_workspace=ws_flag or is_workspace_root(rp),
                    default_segment_key=default_key,
                    active_workstream_hint=hint,
                    segments=segments,
                    worktrees=worktrees,
                )
            )
            logger.debug(
                "[discover] group %s — %d segment(s), %d worktree(s)",
                rp.name, len(segments), len(worktrees),
            )
        logger.info("[discover] returning %d group(s)", len(groups))
        return groups

    def _find_dirs(self, root: Path, name: str) -> list[Path]:
        out: list[Path] = []
        try:
            for dirpath, dirnames, _filenames in os.walk(root, topdown=True):
                dirnames[:] = [d for d in dirnames if d not in _EXCLUDED_DIRS]
                if Path(dirpath).name == name:
                    out.append(Path(dirpath))
        except (PermissionError, OSError):
            pass
        return out

    def _build_gsd1_segment(
        self, ctx: PlanningContext, is_workspace: bool, active_hint: str | None
    ) -> SegmentModel | None:
        base = ctx.planning_base
        roadmap = base / "ROADMAP.md"
        if not roadmap.is_file():
            roadmap = base / "roadmap.md"
        if not roadmap.is_file():
            milestones_dir = base / "milestones"
            has_milestone_roadmaps = milestones_dir.is_dir() and any(milestones_dir.glob("*-ROADMAP.md"))
            if not (base / "phases").is_dir() and not has_milestone_roadmaps:
                return None

        # --- gsd-core DETECTION (per D-02, DETECT-01) ---
        # Primary signal: config.json existence
        config_path = base / "config.json"
        config_data = _try_read_json(config_path)
        is_gsd_core = config_data is not None

        # Fallback: sniff ROADMAP.md for heading-based phase format.
        # Skip sniff when .planning/phases/ exists — that directory is a definitive GSD-1
        # structural marker that takes precedence over ROADMAP heading style.
        if not is_gsd_core and roadmap.is_file() and not (base / "phases").is_dir():
            roadmap_preview = _try_read(roadmap) or ""
            if _HEADING_PHASE_SNIFF.search(roadmap_preview[:2000]):
                is_gsd_core = True

        # Choose parser based on detection
        if roadmap.is_file():
            if is_gsd_core:
                res = GsdCoreRoadmapParser.parse(str(roadmap))
            else:
                res = RoadmapParser.parse(str(roadmap))
        else:
            res = None

        version = GsdVersion.CORE if is_gsd_core else GsdVersion.V1

        if res and res.is_success and res.value:
            proj = res.value
            proj = proj.model_copy(update={"path": str(ctx.repo_root), "version": version})
        else:
            proj = GsdProject(
                name=ctx.repo_root.name,
                path=str(ctx.repo_root),
                version=version,
            )
            if not roadmap.is_file():
                arch = RoadmapParser._try_extract_from_milestone_archives(str(base / "ROADMAP.md"))
                if arch:
                    proj = proj.model_copy(update={"milestones": arch})

        proj = self._enrich_planning(ctx.planning_base, proj)
        proj = self._apply_state_mtime(ctx, proj)

        # --- STATE.md parsing for position and progress metrics ---
        state_position: str | None = None
        for state_name in ("STATE.md", "state.md"):
            state_path = base / state_name
            if state_path.is_file():
                state_result = StateParser.parse(str(state_path))
                if state_result.is_success and state_result.value:
                    si = state_result.value
                    pos = si.status or si.active_slice or ""
                    if pos.strip():
                        state_position = pos.strip()
                    # PROG-01, PROG-02: wire progress fields from StateParser
                    if si.total_phases or si.completed_phases or si.progress_percent:
                        proj = proj.model_copy(
                            update={
                                "total_phases": si.total_phases,
                                "completed_phases": si.completed_phases,
                                "progress_percent": si.progress_percent,
                            }
                        )
                break  # Only try the first existing file

        # --- HANDOFF.JSON (per DOCS-06, D-06) ---
        handoff_path = base / "HANDOFF.json"
        handoff_data = _try_read_json(handoff_path)
        if handoff_data is not None:
            handoff_info = {
                "phase": handoff_data.get("phase", ""),
                "plan": handoff_data.get("plan", ""),
                "timestamp": handoff_data.get("timestamp", ""),
                "paused": True,
            }
            proj = proj.model_copy(update={"handoff_info": handoff_info})

        # --- .CONTINUE-HERE.MD (per DOCS-07) ---
        continue_here_path = base / ".continue-here.md"
        if continue_here_path.is_file():
            proj = proj.model_copy(update={"continue_here": True})

        # --- CONFIG.JSON SURFACING (per DOCS-08, D-07) ---
        if config_data is not None:
            # Extract summary fields with safe .get() defaults (T-11-02 mitigation)
            workflow = config_data.get("workflow") or {}
            git_cfg = config_data.get("git") or {}
            config_info = {
                "workflow_mode": (
                    config_data.get("mode")
                    or workflow.get("discuss_mode")
                ),
                "model_profile": config_data.get("model_profile"),
                "branching_strategy": git_cfg.get("branching_strategy"),
            }
            proj = proj.model_copy(update={"config_info": config_info})

        sm = SegmentModel(
            segment_key=ctx.segment_key,
            gsd_project=ctx.gsd_project,
            workstream=ctx.workstream,
            gsd_version=version,
            planning_path=str(ctx.planning_base),
            repo_root=str(ctx.repo_root),
            project=proj,
            is_workspace=is_workspace,
            state_current_position=state_position,
        )
        return sm

    def _enrich_planning(self, planning_dir: Path, project: GsdProject) -> GsdProject:
        phases_dir = planning_dir / "phases"
        milestones_dir = planning_dir / "milestones"
        if not phases_dir.is_dir() and not milestones_dir.is_dir():
            return project
        phases_dir_use = phases_dir if phases_dir.is_dir() else Path("")

        new_milestones: list[Milestone] = []
        for m in project.milestones:
            enriched_phases: list[PhaseEntry] = []
            phase_list = list(m.phases)

            def enrich_one(p: PhaseEntry) -> PhaseEntry:
                return self._enrich_phase(planning_dir, str(phases_dir_use) if phases_dir_use else "", p)

            if len(phase_list) > 4:
                with ThreadPoolExecutor(max_workers=min(8, len(phase_list))) as ex:
                    futures = {ex.submit(enrich_one, p): p for p in phase_list}
                    for fut in as_completed(futures):
                        enriched_phases.append(fut.result())
                enriched_phases.sort(key=lambda x: x.number)
            else:
                enriched_phases = [enrich_one(p) for p in phase_list]

            new_milestones.append(
                Milestone(
                    title=m.title,
                    number=m.number,
                    status=m.status,
                    progress=m.progress,
                    phases=enriched_phases,
                    code=m.code,
                    vision=m.vision,
                )
            )
        return project.model_copy(update={"milestones": new_milestones})

    def _apply_state_mtime(self, ctx: PlanningContext, project: GsdProject) -> GsdProject:
        base = ctx.planning_base
        best: datetime | None = None
        for state_name in ("STATE.md", "state.md"):
            sp = base / state_name
            if sp.is_file():
                try:
                    lu = datetime.fromtimestamp(sp.stat().st_mtime, tz=timezone.utc)
                    if best is None or lu > best:
                        best = lu
                except OSError:
                    pass
        if best is None:
            return project
        old = project.last_updated
        if old is None:
            return project.model_copy(update={"last_updated": best})
        o = old.replace(tzinfo=None) if old.tzinfo else old
        b = best.replace(tzinfo=None) if best.tzinfo else best
        if b > o:
            return project.model_copy(update={"last_updated": best})
        return project

    def _enrich_phase(self, planning_dir: Path, phases_dir: str, phase: PhaseEntry) -> PhaseEntry:
        try:
            padded = f"{phase.number:02d}"
            phase_dir: Path | None = None
            is_archived = False
            archive_milestone = None
            archive_root = None

            if phases_dir and Path(phases_dir).is_dir():
                for d in Path(phases_dir).iterdir():
                    if d.is_dir() and d.name.lower().startswith(padded + "-"):
                        phase_dir = d
                        break

            if phase_dir is None:
                found = self._find_archive_phase_dir(planning_dir, padded)
                if found:
                    phase_dir, archive_milestone = found
                    is_archived = True
                    archive_root = str(phase_dir)

            if phase_dir is None:
                return phase

            plan_files = sorted(phase_dir.glob("*-PLAN.md"), reverse=True)
            latest_plan = plan_files[0] if plan_files else None
            plan_content = ""
            todos: list[TodoItem] = []
            if latest_plan:
                pr = PlanParser.parse(str(latest_plan))
                if pr.is_success and pr.value:
                    raw = latest_plan.read_text(encoding="utf-8", errors="replace")
                    plan_content = _strip_frontmatter(raw)
                    todos = pr.value.todos

            artifacts = sorted(str(f) for f in phase_dir.glob("*.md"))
            summary_files = list(phase_dir.glob("*-SUMMARY.md"))
            last_updated = None
            if summary_files:
                last_updated = max(
                    datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc) for f in summary_files
                )
            elif latest_plan:
                last_updated = datetime.fromtimestamp(latest_plan.stat().st_mtime, tz=timezone.utc)

            latest_plan_write = None
            if plan_files:
                latest_plan_write = max(
                    datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc) for f in plan_files
                )

            validation_file = _resolve_artifact(phase_dir, padded, "VALIDATION.md")
            verification_file = _resolve_artifact(phase_dir, padded, "VERIFICATION.md")
            nyq = self._read_nyquist(validation_file)
            final_status = phase.status
            if nyq is False and phase.status in (PhaseStatus.IN_PROGRESS, PhaseStatus.COMPLETE):
                final_status = PhaseStatus.NEEDS_VERIFICATION

            ctx_file = _resolve_artifact(phase_dir, padded, "CONTEXT.md")
            research_file = _resolve_artifact(phase_dir, padded, "RESEARCH.md")
            uat_file = _resolve_artifact(phase_dir, padded, "UAT.md")
            ui_spec_file = _resolve_artifact(phase_dir, padded, "UI-SPEC.md")
            ui_review_file = _resolve_artifact(phase_dir, padded, "UI-REVIEW.md")

            has_context = ctx_file.is_file()
            has_research = research_file.is_file()
            has_plan = len(plan_files) > 0
            has_uat = uat_file.is_file()
            has_validation = validation_file.is_file() or verification_file.is_file()
            has_ui_spec = ui_spec_file.is_file()
            has_ui_review = ui_review_file.is_file()
            has_summary = len(summary_files) > 0
            # has_requirements: project-level REQUIREMENTS.md in planning_dir
            has_requirements = (planning_dir / "REQUIREMENTS.md").is_file()

            if not has_research:
                coverage = ResearchCoverage.NONE
            elif summary_files:
                coverage = ResearchCoverage.COMPLETE
            else:
                coverage = ResearchCoverage.PARTIAL

            research_content = _try_read(research_file) if has_research else None
            validation_content = _try_read(validation_file) or (_try_read(verification_file) if verification_file.is_file() else None)

            return PhaseEntry(
                number=phase.number,
                code=phase.code,
                title=phase.title,
                status=final_status,
                drift=_compute_drift(final_status, latest_plan_write, last_updated),
                plan_write_time=latest_plan_write,
                goal=phase.goal,
                plan_content=plan_content,
                todos=todos,
                artifact_paths=artifacts,
                last_updated=last_updated,
                has_context=has_context,
                has_research=has_research,
                has_plan=has_plan,
                has_uat=has_uat,
                has_validation=has_validation,
                has_ui_spec=has_ui_spec,
                has_ui_review=has_ui_review,
                has_summary=has_summary,
                has_requirements=has_requirements,
                nyquist_compliant=nyq,
                research_coverage=coverage,
                research_content=research_content,
                validation_content=validation_content,
                is_archived=is_archived,
                archive_milestone=archive_milestone,
                archive_root=archive_root,
            )
        except Exception as ex:
            logger.warning("Failed to enrich phase %s in %s: %s", phase.number, planning_dir, ex)
            return phase

    def _find_archive_phase_dir(
        self, planning_dir: Path, padded_num: str
    ) -> tuple[Path, str] | None:
        try:
            milestones_dir = planning_dir / "milestones"
            if not milestones_dir.is_dir():
                return None
            containers = sorted(
                [p for p in milestones_dir.iterdir() if p.is_dir() and p.name.endswith("-phases")],
                reverse=True,
            )
            for container in containers:
                for d in container.iterdir():
                    if d.is_dir() and d.name.lower().startswith(padded_num + "-"):
                        ver = container.name[: -len("-phases")] if container.name.endswith("-phases") else container.name
                        return d, ver
            return None
        except Exception as ex:
            logger.warning("Failed to search archive phase dirs under %s: %s", planning_dir, ex)
            return None

    @staticmethod
    def _read_nyquist(path: Path) -> bool | None:
        try:
            if not path.is_file():
                return None
            text = path.read_text(encoding="utf-8", errors="replace")
            m = _NYQUIST.search(text)
            if not m:
                return None
            return m.group(1).lower() == "true"
        except OSError:
            return None
