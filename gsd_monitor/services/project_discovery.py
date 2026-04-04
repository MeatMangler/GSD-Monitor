"""Discover GSD projects with GSD-1 (multi-context) + GSD-2 — ports WinGsdMonitor.Core logic."""

from __future__ import annotations

import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from gsd_monitor.models.core import GsdProject, Milestone, PhaseEntry, TodoItem
from gsd_monitor.models.enums import (
    DriftIndicator,
    GsdVersion,
    MilestoneStatus,
    PhaseStatus,
    ResearchCoverage,
)
from gsd_monitor.parsers.gsd2_roadmap import Gsd2RoadmapParser
from gsd_monitor.parsers.plan_parser import PlanParser
from gsd_monitor.parsers.roadmap import RoadmapParser
from gsd_monitor.parsers.state_parser import StateParser
from gsd_monitor.services.git_service import GitService
from gsd_monitor.services.planning_layout import PlanningContext, iter_planning_contexts, is_workspace_root

_FRONTMATTER = re.compile(r"^---\s*\n.*?^---\s*\n", re.DOTALL | re.MULTILINE)
_NYQUIST = re.compile(r"nyquist_compliant:\s*(true|false)", re.IGNORECASE)
_VERIFICATION = re.compile(r"verification_result:\s*(pass|fail)", re.IGNORECASE)
_EXCLUDED_DIRS: set[str] = {"node_modules", ".venv", ".git", "build", "dist"}


def _try_read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _strip_frontmatter(raw: str) -> str:
    m = _FRONTMATTER.match(raw)
    if m:
        return raw[m.end() :].lstrip()
    return raw


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
        except Exception:
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
        by_repo: dict[str, list[SegmentModel]] = {}
        gsd2_repos: set[str] = set()
        by_repo_worktrees: dict[str, list[tuple[Path, bool]]] = {}

        for root in roots:
            root_path = Path(root).resolve()
            try:
                for gsd_dir in self._find_dirs(root_path, ".gsd"):
                    repo_dir = gsd_dir.parent
                    canonical = _resolve_canonical_root(repo_dir)
                    canon_key = str(canonical)
                    is_primary = (repo_dir / ".git").is_dir()
                    seg = self._discover_gsd2(repo_dir, gsd_dir)
                    if seg:
                        by_repo.setdefault(canon_key, []).append(seg)
                        gsd2_repos.add(canon_key)
                        wt_list = by_repo_worktrees.setdefault(canon_key, [])
                        if not any(str(p) == str(repo_dir) for p, _ in wt_list):
                            wt_list.append((repo_dir, is_primary))
            except PermissionError:
                continue

        for root in roots:
            root_path = Path(root).resolve()
            try:
                for planning_dir in self._find_dirs(root_path, ".planning"):
                    if planning_dir.name != ".planning":
                        continue
                    repo_dir = planning_dir.parent
                    canonical = _resolve_canonical_root(repo_dir)
                    canon_key = str(canonical)
                    if canon_key in gsd2_repos:
                        continue
                    # Accumulate worktree info regardless of segment deduplication
                    is_primary = (repo_dir / ".git").is_dir()
                    wt_list = by_repo_worktrees.setdefault(canon_key, [])
                    if not any(str(p) == str(repo_dir) for p, _ in wt_list):
                        wt_list.append((repo_dir, is_primary))
                    # Only add segments from the first worktree discovered for this canonical root
                    if canon_key in by_repo:
                        continue
                    hint_t = _try_read(repo_dir / ".planning" / "active-workstream")
                    hint = hint_t.strip() if hint_t else None
                    ws = is_workspace_root(repo_dir)
                    for ctx in iter_planning_contexts(planning_dir, repo_dir):
                        seg = self._build_gsd1_segment(ctx, ws, hint)
                        if seg:
                            by_repo.setdefault(canon_key, []).append(seg)
            except PermissionError:
                continue

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

    def _read_active_workstream(self, planning_dir: Path) -> str | None:
        f = planning_dir / "active-workstream"
        t = _try_read(f)
        return t.strip() if t else None

    def _build_gsd1_segment(
        self, ctx: PlanningContext, is_workspace: bool, active_hint: str | None
    ) -> SegmentModel | None:
        base = ctx.planning_base
        roadmap = base / "ROADMAP.md"
        if not roadmap.is_file():
            if not (base / "phases").is_dir():
                return None
        res = RoadmapParser.parse(str(roadmap)) if roadmap.is_file() else None
        if res and res.is_success and res.value:
            proj = res.value
            proj = proj.model_copy(update={"path": str(ctx.repo_root)})
        else:
            proj = GsdProject(
                name=ctx.repo_root.name,
                path=str(ctx.repo_root),
                version=GsdVersion.V1,
            )
        proj = self._enrich_planning(ctx.planning_base, proj)
        proj = self._apply_state_mtime(ctx, proj)

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
            segment_key=ctx.segment_key,
            gsd_project=ctx.gsd_project,
            workstream=ctx.workstream,
            gsd_version=GsdVersion.V1,
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
                    lu = datetime.utcfromtimestamp(sp.stat().st_mtime)
                    if best is None or lu > best:
                        best = lu
                except Exception:
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

            artifacts = sorted(
                [
                    str(f)
                    for f in phase_dir.glob("*.md")
                    if f.name.endswith("-PLAN.md") or f.name.endswith("-SUMMARY.md")
                ]
            )
            summary_files = list(phase_dir.glob("*-SUMMARY.md"))
            last_updated = None
            if summary_files:
                last_updated = max(
                    datetime.utcfromtimestamp(f.stat().st_mtime) for f in summary_files
                )
            elif latest_plan:
                last_updated = datetime.utcfromtimestamp(latest_plan.stat().st_mtime)

            latest_plan_write = None
            if plan_files:
                latest_plan_write = max(
                    datetime.utcfromtimestamp(f.stat().st_mtime) for f in plan_files
                )

            validation_file = phase_dir / f"{padded}-VALIDATION.md"
            nyq = self._read_nyquist(validation_file)
            final_status = phase.status
            if nyq is False and phase.status in (PhaseStatus.IN_PROGRESS, PhaseStatus.COMPLETE):
                final_status = PhaseStatus.NEEDS_VERIFICATION

            ctx_file = phase_dir / f"{padded}-CONTEXT.md"
            research_file = phase_dir / f"{padded}-RESEARCH.md"
            has_context = ctx_file.is_file()
            has_research = research_file.is_file()
            has_plan = len(plan_files) > 0
            has_validation = validation_file.is_file()

            if not has_research:
                coverage = ResearchCoverage.NONE
            elif summary_files:
                coverage = ResearchCoverage.COMPLETE
            else:
                coverage = ResearchCoverage.PARTIAL

            research_content = _try_read(research_file) if has_research else None
            validation_content = _try_read(validation_file) if has_validation else None

            return PhaseEntry(
                number=phase.number,
                title=phase.title,
                status=final_status,
                drift=DriftIndicator.DEFERRED,
                plan_write_time=latest_plan_write,
                goal=phase.goal,
                plan_content=plan_content,
                todos=todos,
                artifact_paths=artifacts,
                last_updated=last_updated,
                has_context=has_context,
                has_research=has_research,
                has_plan=has_plan,
                has_validation=has_validation,
                nyquist_compliant=nyq,
                research_coverage=coverage,
                research_content=research_content,
                validation_content=validation_content,
                is_archived=is_archived,
                archive_milestone=archive_milestone,
                archive_root=archive_root,
            )
        except Exception:
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
        except Exception:
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
        except Exception:
            return None

    def _discover_gsd2(self, repo_dir: Path, gsd_dir: Path) -> SegmentModel | None:
        try:
            name = repo_dir.name
            milestones: list[Milestone] = []
            m_root = gsd_dir / "milestones"
            if m_root.is_dir():
                m_dirs = sorted(
                    [p for p in m_root.iterdir() if p.is_dir() and len(p.name) >= 3 and p.name.startswith("M")],
                    key=lambda p: p.name.lower(),
                )
                for ordinal, m_dir in enumerate(m_dirs, start=1):
                    roadmap = m_dir / "roadmap.md"
                    if not roadmap.is_file():
                        continue
                    pr = Gsd2RoadmapParser.parse(str(roadmap))
                    if not pr.is_success or not pr.value:
                        continue
                    g2 = pr.value
                    phases: list[PhaseEntry] = []
                    for s in g2.slices:
                        n = 0
                        if len(s.code) > 1 and s.code[1:].isdigit():
                            n = int(s.code[1:])
                        phases.append(
                            PhaseEntry(
                                number=n,
                                code=s.code,
                                title=s.title,
                                status=PhaseStatus.COMPLETE if s.is_complete else PhaseStatus.NOT_STARTED,
                                goal=s.demo_sentence,
                                risk_tag=s.risk_tag,
                                depends_on=s.depends_on,
                            )
                        )
                    total = len(phases)
                    completed = sum(1 for p in phases if p.status == PhaseStatus.COMPLETE)
                    if total == 0:
                        mst = MilestoneStatus.PLANNED
                    elif completed == total:
                        mst = MilestoneStatus.COMPLETED
                    elif completed > 0:
                        mst = MilestoneStatus.ACTIVE
                    else:
                        mst = MilestoneStatus.PLANNED
                    progress = 0 if total == 0 else int(round(completed * 100.0 / total))
                    milestones.append(
                        Milestone(
                            number=ordinal,
                            title=m_dir.name,
                            code=g2.code,
                            vision=g2.vision,
                            status=mst,
                            progress=progress,
                            phases=phases,
                        )
                    )
            proj = GsdProject(name=name, path=str(repo_dir), version=GsdVersion.V2, milestones=milestones)
            state_path = gsd_dir / "state.md"
            if state_path.is_file():
                try:
                    lu = datetime.utcfromtimestamp(state_path.stat().st_mtime)
                    proj = proj.model_copy(update={"last_updated": lu})
                except Exception:
                    pass
            proj = self._enrich_gsd2_project(gsd_dir, proj)
            return SegmentModel(
                segment_key="gsd2",
                gsd_project=None,
                workstream=None,
                gsd_version=GsdVersion.V2,
                planning_path=str(gsd_dir),
                repo_root=str(repo_dir),
                project=proj,
            )
        except Exception:
            return SegmentModel(
                segment_key="gsd2",
                gsd_project=None,
                workstream=None,
                gsd_version=GsdVersion.V2,
                planning_path=str(gsd_dir),
                repo_root=str(repo_dir),
                project=GsdProject(name=repo_dir.name, path=str(repo_dir), version=GsdVersion.V2),
            )

    def _enrich_gsd2_project(self, gsd_dir: Path, project: GsdProject) -> GsdProject:
        new_ms: list[Milestone] = []
        for m in project.milestones:
            mcode = m.code or m.title
            new_phases = [self._enrich_gsd2_slice(gsd_dir, mcode, p) for p in m.phases]
            new_ms.append(m.model_copy(update={"phases": new_phases}))
        return project.model_copy(update={"milestones": new_ms})

    def _enrich_gsd2_slice(self, gsd_dir: Path, milestone_code: str | None, sl: PhaseEntry) -> PhaseEntry:
        try:
            if not milestone_code or not sl.code:
                return sl
            slice_dir = gsd_dir / "milestones" / milestone_code / "slices" / sl.code
            if not slice_dir.is_dir():
                return sl
            plan_file = slice_dir / "plan.md"
            context_file = slice_dir / "context.md"
            research_file = slice_dir / "research.md"
            uat_file = slice_dir / "uat.md"
            summary_file = slice_dir / "summary.md"
            has_plan = plan_file.is_file()
            has_context = context_file.is_file()
            has_research = research_file.is_file()
            has_uat = uat_file.is_file()
            last_updated = None
            if summary_file.is_file():
                try:
                    last_updated = datetime.utcfromtimestamp(summary_file.stat().st_mtime)
                except Exception:
                    pass
            plan_content = None
            if has_plan:
                raw = _try_read(plan_file)
                if raw:
                    plan_content = _strip_frontmatter(raw)
            artifact_paths = sorted(
                str(p)
                for p in [plan_file, summary_file, research_file, context_file, uat_file]
                if p.is_file()
            )
            plan_write_time = None
            if has_plan:
                try:
                    plan_write_time = datetime.utcfromtimestamp(plan_file.stat().st_mtime)
                except Exception:
                    pass
            tasks_dir = slice_dir / "tasks"
            nyq: bool | None = None
            final_status = sl.status
            if tasks_dir.is_dir():
                summaries = sorted(tasks_dir.glob("T*-summary.md"))
                if summaries:
                    any_fail = False
                    all_pass = True
                    for tf in summaries:
                        txt = _try_read(tf)
                        if not txt:
                            continue
                        vm = _VERIFICATION.search(txt)
                        if not vm:
                            all_pass = False
                            continue
                        if vm.group(1).lower() == "fail":
                            any_fail = True
                            all_pass = False
                    if any_fail:
                        nyq = False
                        if sl.status in (PhaseStatus.IN_PROGRESS, PhaseStatus.COMPLETE):
                            final_status = PhaseStatus.NEEDS_VERIFICATION
                    elif all_pass:
                        nyq = True
            research_content = _try_read(research_file) if has_research else None
            return sl.model_copy(
                update={
                    "status": final_status,
                    "drift": DriftIndicator.DEFERRED,
                    "plan_write_time": plan_write_time,
                    "has_plan": has_plan,
                    "has_context": has_context,
                    "has_research": has_research,
                    "has_uat": has_uat,
                    "has_validation": False,
                    "nyquist_compliant": nyq,
                    "plan_content": plan_content,
                    "artifact_paths": artifact_paths,
                    "last_updated": last_updated,
                    "research_content": research_content,
                }
            )
        except Exception:
            return sl
