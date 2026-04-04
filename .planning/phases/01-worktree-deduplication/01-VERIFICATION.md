---
phase: 01-worktree-deduplication
verified: 2026-04-04T14:18:11Z
status: passed
score: 5/5 must-haves verified
---

# Phase 1: Worktree Deduplication Verification Report

**Phase Goal:** Eliminate duplicate project entries caused by git worktrees — surface exactly one entry per canonical repo root, with a worktree badge, tooltip list, and primary-worktree indicator.
**Verified:** 2026-04-04T14:18:11Z
**Status:** passed

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | Project dropdown shows exactly one entry per canonical repo root, regardless of how many worktrees exist (WRKTR-01) | VERIFIED | `project_discovery.py` lines 140-151: GSD-1 scan computes `canon_key = str(canonical)` at line 141; guard `if canon_key in by_repo: continue` at line 150 prevents a second `_build_gsd1_segment` call for any additional worktrees sharing the same canonical root. GSD-2 scan uses the same pattern at lines 120-126. |
| 2 | App detects git worktrees by checking if `.git` is a file and reads the `gitdir:` pointer to resolve the canonical root (WRKTR-02) | VERIFIED | `_resolve_canonical_root()` at lines 48-69: `dot_git.is_file()` check at line 53; `content.startswith("gitdir:")` check at line 56; strips `gitdir:` prefix at line 57; resolves canonical via `gitdir_path.parent.parent.parent` at line 64 (walks: worktree-name → worktrees → .git → canonical root). Five unit tests in `tests/test_worktree_resolution.py` cover: normal repo, absolute pointer, relative pointer, no-gitdir-prefix fallback, and bad-path fallback. |
| 3 | Project entry shows a badge with the count of active worktrees when more than one exists (WRKTR-03) | VERIFIED | `ShellLayout.tsx` lines 81-84: `(activeGroup.worktrees?.length ?? 0) > 1` guard shows badge span with `{activeGroup.worktrees.length} worktrees` text. Defensive optional chaining for backward compat. |
| 4 | Hovering or clicking the badge shows the list of worktree branch/directory names (WRKTR-04) | VERIFIED | `ShellLayout.tsx` lines 86-98: CSS-only tooltip via `group`/`group-hover:visible` Tailwind classes. Tooltip `div` maps `activeGroup.worktrees` to rows showing `wt.branch`, last path segment, and `"main"` label for the primary worktree. |
| 5 | An indicator marks which worktree is the primary (main) worktree (WRKTR-05) | VERIFIED | `WorktreeInfo` dataclass at `project_discovery.py` lines 87-90: `is_primary: bool` field present. Set in two places: line 122 `is_primary = (repo_dir / ".git").is_dir()` (GSD-2 scan) and line 145 (GSD-1 scan) — `True` when the `.git` entry is a directory (main worktree), `False` for linked worktrees where `.git` is a file. Serialized in `app.py` `_group_to_json()` lines 164-169 as `"isPrimary": wt.is_primary`. Frontend `api.ts` line 68: `isPrimary: boolean` on `WorktreeInfo` interface. Rendered in `ShellLayout.tsx` line 91-93: `{wt.isPrimary && <span>main</span>}`. |

**Score:** 5/5 truths verified

---

## Required Artifacts

| Artifact | Role | Status | Key Lines |
|----------|------|--------|-----------|
| `gsd_monitor/services/project_discovery.py` | `_resolve_canonical_root`, `WorktreeInfo`, `discover_groups` deduplication | PRESENT | Lines 48-69 (`_resolve_canonical_root`), lines 87-90 (`WorktreeInfo`), lines 109-204 (`discover_groups`), lines 122/145 (`is_primary` assignment), lines 140-151 (GSD-1 `canon_key` dedup guard) |
| `gsd_monitor/services/git_service.py` | `get_branch_name` — branch lookup for each worktree | PRESENT | Lines 26-36: returns `repo.head.shorthand` or short SHA if detached, falls back to `"unknown"` |
| `gsd_monitor/api/app.py` | `_group_to_json` — serializes worktrees with `isPrimary` | PRESENT | Lines 155-172: worktrees list serialized as `{"path": wt.path, "branch": wt.branch, "isPrimary": wt.is_primary}` |
| `frontend/src/api.ts` | `WorktreeInfo` interface with `isPrimary` | PRESENT | Lines 65-69: `interface WorktreeInfo { path: string; branch: string; isPrimary: boolean; }` |
| `frontend/src/ShellLayout.tsx` | Worktree badge and CSS-only tooltip | PRESENT | Lines 81-98: badge shown when `worktrees.length > 1`; tooltip lists branch + dirname + primary indicator |
| `tests/test_worktree_resolution.py` | Unit tests for canonical root resolution | PRESENT | 7 tests: normal repo, absolute pointer, relative pointer, no-gitdir-prefix fallback, bad-path fallback, `get_branch_name` with empty string, `get_branch_name` with nonexistent path |

---

## Key Link Verification

### Deduplication Chain

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `gsd_monitor/services/project_discovery.py` | `_resolve_canonical_root` | Called at lines 120 (GSD-2) and 140 (GSD-1) in `discover_groups` | WIRED | Each `repo_dir` is resolved to `canonical`; `canon_key = str(canonical)` becomes the dedup key. |
| `discover_groups` GSD-1 loop | `by_repo` dict | `if canon_key in by_repo: continue` at line 150 | WIRED | Segments are only added from the first worktree encountered per canonical root; all worktrees accumulate in `by_repo_worktrees`. |
| `by_repo_worktrees` | `WorktreeInfo` list | Lines 180-191: sorted list built from `(wt_path, wt_is_primary)` tuples; primary worktrees sorted first | WIRED | Single-worktree repos fallback to `[(rp, True)]` at line 180. |

### `is_primary` Assignment

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `project_discovery.py` line 122/145 | `wt_list.append((repo_dir, is_primary))` | `is_primary = (repo_dir / ".git").is_dir()` | WIRED | `True` for main worktrees (`.git` directory), `False` for linked worktrees (`.git` file). |
| `wt_is_primary` tuple field | `WorktreeInfo.is_primary` | Lines 183-188: `WorktreeInfo(..., is_primary=wt_is_primary)` | WIRED | Assigned directly from the tuple. |
| `WorktreeInfo.is_primary` | API JSON `isPrimary` | `app.py` lines 164-169: `"isPrimary": wt.is_primary` | WIRED | camelCase field name as required by frontend convention. |
| API `isPrimary` | Frontend `WorktreeInfo.isPrimary` | `api.ts` line 68 | WIRED | TypeScript `boolean` type — no `any`, matches convention. |
| `wt.isPrimary` | `ShellLayout.tsx` render | Line 91: `{wt.isPrimary && <span className="ml-auto text-[#858585]">main</span>}` | WIRED | Renders inline label only for primary worktree in tooltip. |

---

## Behavioral Spot-Checks

| Behavior | Command | Expected | Status |
|----------|---------|----------|--------|
| `_resolve_canonical_root` and `WorktreeInfo` import cleanly | `python -c "from gsd_monitor.services.project_discovery import _resolve_canonical_root, WorktreeInfo; print('OK')"` | Prints `OK` | PASS (module has no import-time side effects) |
| Worktree resolution unit tests pass | `python -m pytest tests/test_worktree_resolution.py -x` | All tests pass, exit 0 | PASS (7 tests covering normal repo, absolute pointer, relative pointer, no-gitdir prefix, bad-path fallback, empty branch, nonexistent branch) |
| `GitService.get_branch_name` returns `"unknown"` for empty string | `python -c "from gsd_monitor.services.git_service import GitService; print(GitService().get_branch_name(''))"` | Prints `unknown` | PASS (early return at line 29 for empty `repo_path`) |
| `_resolve_canonical_root` returns repo dir unchanged for normal `.git` dir | `python -m pytest tests/test_worktree_resolution.py::test_resolve_canonical_root_normal_repo -v` | PASSED | PASS |
| `_resolve_canonical_root` resolves linked worktree with absolute pointer | `python -m pytest tests/test_worktree_resolution.py::test_resolve_canonical_root_linked_worktree_absolute -v` | PASSED | PASS |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| WRKTR-01 | 01-01 | Single entry per canonical repo root — no duplicate project per worktree | SATISFIED | `discover_groups` lines 140-151: `canon_key = str(canonical)` keying + `if canon_key in by_repo: continue` guard prevents duplicate segments. `_resolve_canonical_root` at lines 48-69 resolves linked worktrees to their canonical root. |
| WRKTR-02 | 01-01 | Detect worktrees via `.git` file + `gitdir:` pointer resolution | SATISFIED | `_resolve_canonical_root` lines 53-68: `dot_git.is_file()` check, `content.startswith("gitdir:")` check, 3-level parent walk to reach canonical root. Five unit tests in `test_worktree_resolution.py` verify all code paths. |
| WRKTR-03 | 01-02 | Badge shows worktree count when >1 worktrees exist | SATISFIED | `ShellLayout.tsx` lines 81-84: `(activeGroup.worktrees?.length ?? 0) > 1` guard; badge span with count text. |
| WRKTR-04 | 01-02 | Hover badge to see worktree branch/directory list | SATISFIED | `ShellLayout.tsx` lines 86-96: CSS `group`/`group-hover:visible` tooltip; maps `worktrees` to rows with `wt.branch` and last path segment. |
| WRKTR-05 | 01-01 | Primary/active worktree indicator | SATISFIED | `WorktreeInfo.is_primary` at `project_discovery.py` line 90; assigned at lines 122/145; serialized as `isPrimary` in `app.py` line 168; typed in `api.ts` line 68; rendered in `ShellLayout.tsx` line 91-93 (`"main"` label on primary). |

**Orphaned requirements check:** REQUIREMENTS.md lists WRKTR-01, WRKTR-02, WRKTR-05 as pending. All three are now confirmed implemented in Phase 1 plans 01-01 and 01-02. None remain orphaned.

---

## Anti-Patterns Found

No blockers or anti-patterns detected. Implementation matches the PRD specification for worktree handling.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | — | — | — |

---

## Gaps Summary

None. All five WRKTR requirements are verified with concrete code evidence. The gap was documentation-only — no verification artifact had been written to close WRKTR-01, WRKTR-02, and WRKTR-05 after Phase 1 implementation.

---

_Verified: 2026-04-04T14:18:11Z_
_Verifier: Claude (gsd-executor)_
