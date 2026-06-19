"""pygit2-backed git queries — mirrors LibGit2SharpGitService."""

from __future__ import annotations

import pygit2


class GitService:
    def get_branch_name(self, repo_path: str) -> str:
        """Return current branch shorthand, or short SHA if detached, or 'unknown'."""
        if not repo_path:
            return "unknown"
        try:
            repo = pygit2.Repository(repo_path)
            if repo.head_is_detached:
                return str(repo.head.target)[:7]
            return repo.head.shorthand
        except Exception:
            return "unknown"
