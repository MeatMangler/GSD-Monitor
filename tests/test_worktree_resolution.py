"""Unit tests for _resolve_canonical_root and GitService.get_branch_name."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_resolve_canonical_root_normal_repo(tmp_path: Path) -> None:
    """_resolve_canonical_root returns repo_dir unchanged when .git is a directory."""
    dot_git = tmp_path / ".git"
    dot_git.mkdir()

    from gsd_monitor.services.project_discovery import _resolve_canonical_root

    result = _resolve_canonical_root(tmp_path)
    assert result == tmp_path


def test_resolve_canonical_root_linked_worktree_absolute(tmp_path: Path) -> None:
    """_resolve_canonical_root reads .git file with absolute gitdir pointer."""
    # Set up canonical repo structure
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    canonical_dot_git = canonical / ".git"
    canonical_dot_git.mkdir()
    worktrees_dir = canonical_dot_git / "worktrees" / "feature"
    worktrees_dir.mkdir(parents=True)

    # Set up linked worktree
    linked = tmp_path / "linked"
    linked.mkdir()
    dot_git_file = linked / ".git"
    dot_git_file.write_text(
        f"gitdir: {str(worktrees_dir)}", encoding="utf-8"
    )

    from gsd_monitor.services.project_discovery import _resolve_canonical_root

    result = _resolve_canonical_root(linked)
    assert result == canonical


def test_resolve_canonical_root_linked_worktree_relative(tmp_path: Path) -> None:
    """_resolve_canonical_root handles relative gitdir path."""
    # Set up canonical repo structure at same level
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    canonical_dot_git = canonical / ".git"
    canonical_dot_git.mkdir()
    worktrees_dir = canonical_dot_git / "worktrees" / "feature"
    worktrees_dir.mkdir(parents=True)

    # Set up linked worktree next to canonical
    linked = tmp_path / "linked"
    linked.mkdir()
    # Relative path from linked/ to canonical/.git/worktrees/feature
    # is ../canonical/.git/worktrees/feature
    relative = "../canonical/.git/worktrees/feature"
    dot_git_file = linked / ".git"
    dot_git_file.write_text(f"gitdir: {relative}", encoding="utf-8")

    from gsd_monitor.services.project_discovery import _resolve_canonical_root

    result = _resolve_canonical_root(linked)
    assert result == canonical


def test_resolve_canonical_root_no_gitdir_prefix(tmp_path: Path) -> None:
    """_resolve_canonical_root returns repo_dir when .git file has no 'gitdir:' prefix."""
    dot_git_file = tmp_path / ".git"
    dot_git_file.write_text("something else entirely", encoding="utf-8")

    from gsd_monitor.services.project_discovery import _resolve_canonical_root

    result = _resolve_canonical_root(tmp_path)
    assert result == tmp_path


def test_resolve_canonical_root_exception_fallback(tmp_path: Path) -> None:
    """_resolve_canonical_root returns repo_dir as fallback when .git file read raises."""
    dot_git_file = tmp_path / ".git"
    # Write a valid-looking file but point gitdir to a nonexistent path
    dot_git_file.write_text("gitdir: /nonexistent/path/.git/worktrees/x", encoding="utf-8")

    from gsd_monitor.services.project_discovery import _resolve_canonical_root

    # /nonexistent/path is not a directory, so canonical.is_dir() == False
    # Should fall back to returning repo_dir
    result = _resolve_canonical_root(tmp_path)
    assert result == tmp_path


def test_get_branch_name_nonexistent_path() -> None:
    """GitService.get_branch_name returns 'unknown' for non-existent path."""
    from gsd_monitor.services.git_service import GitService

    svc = GitService()
    result = svc.get_branch_name("/nonexistent/path/to/repo")
    assert result == "unknown"


def test_get_branch_name_empty_string() -> None:
    """GitService.get_branch_name returns 'unknown' for empty string."""
    from gsd_monitor.services.git_service import GitService

    svc = GitService()
    result = svc.get_branch_name("")
    assert result == "unknown"
