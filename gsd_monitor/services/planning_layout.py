"""Enumerate GSD planning contexts under a `.planning/` directory (flat, workstreams, multi-project)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


RESERVED = frozenset(
    {
        "workstreams",
        "milestones",
        "research",
        "quick",
        "seeds",
        "threads",
        "forensics",
        "ui-reviews",
        "codebase",
    }
)


@dataclass(frozen=True)
class PlanningContext:
    """One selectable planning slice (grouped + selectors)."""

    planning_base: Path
    repo_root: Path
    gsd_project: str | None
    workstream: str | None
    segment_key: str


def _looks_like_slice(path: Path) -> bool:
    return (
        (path / "STATE.md").is_file()
        or (path / "state.md").is_file()
        or (path / "ROADMAP.md").is_file()
        or (path / "roadmap.md").is_file()
        or (path / "phases").is_dir()
    )


def iter_planning_contexts(planning_root: Path, repo_root: Path) -> list[PlanningContext]:
    """Return all planning bases (flat, workstreams, .planning/{project}/…)."""
    pr = planning_root.resolve()
    out: list[PlanningContext] = []

    has_flat = (pr / "ROADMAP.md").is_file() or (pr / "phases").is_dir()
    if has_flat:
        out.append(
            PlanningContext(
                planning_base=pr,
                repo_root=repo_root,
                gsd_project=None,
                workstream=None,
                segment_key="flat",
            )
        )

    ws_root = pr / "workstreams"
    if ws_root.is_dir():
        for d in sorted([p for p in ws_root.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
            if _looks_like_slice(d):
                out.append(
                    PlanningContext(
                        planning_base=d,
                        repo_root=repo_root,
                        gsd_project=None,
                        workstream=d.name,
                        segment_key=f"ws:{d.name}",
                    )
                )

    for d in sorted([p for p in pr.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        if d.name in RESERVED or d.name == "workstreams":
            continue
        if _looks_like_slice(d):
            out.append(
                PlanningContext(
                    planning_base=d,
                    repo_root=repo_root,
                    gsd_project=d.name,
                    workstream=None,
                    segment_key=f"proj:{d.name}",
                )
            )
            wsr = d / "workstreams"
            if wsr.is_dir():
                for wd in sorted([p for p in wsr.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
                    if _looks_like_slice(wd):
                        out.append(
                            PlanningContext(
                                planning_base=wd,
                                repo_root=repo_root,
                                gsd_project=d.name,
                                workstream=wd.name,
                                segment_key=f"proj:{d.name}/ws:{wd.name}",
                            )
                        )

    if not out and _looks_like_slice(pr):
        out.append(
            PlanningContext(
                planning_base=pr,
                repo_root=repo_root,
                gsd_project=None,
                workstream=None,
                segment_key="flat",
            )
        )

    return out


def is_workspace_root(path: Path) -> bool:
    return (path / "WORKSPACE.md").is_file()
