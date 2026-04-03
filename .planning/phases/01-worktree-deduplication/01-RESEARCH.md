# Phase 1: Worktree Deduplication - Research

**Researched:** 2026-04-03
**Domain:** Git worktree detection (Python/pygit2) + FastAPI dataclass extension + React Tailwind CSS tooltip
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Detect git worktrees by checking if `.git` is a FILE (not a directory) at the scanned path
- **D-02:** Read the `gitdir:` line from the `.git` file to resolve the canonical repo root path
- **D-03:** All worktree paths that resolve to the same canonical root become a single `ProjectGroup`
- **D-04:** The `ProjectGroup.root_path` is set to the canonical root (where `.git` is a directory)
- **D-05:** Add `worktrees: WorktreeInfo[]` to `GroupPayload` (and corresponding backend dataclass)
- **D-06:** `WorktreeInfo` = `{ path: string; branch: string; isPrimary: boolean }` — `isPrimary: true` when `.git` is a directory
- **D-07:** If a repo has only one worktree, `worktrees` has one entry with `isPrimary: true` — badge NOT shown (only show when count > 1)
- **D-08:** Use pygit2 to read branch shorthand — `pygit2.Repository(worktree_path).head.shorthand`
- **D-09:** If HEAD is detached, fall back to the short SHA
- **D-10:** If pygit2 raises (not a git repo or corrupted), skip branch info — use `"unknown"`
- **D-11:** Badge shows worktree count (e.g., "3 worktrees") only when `worktrees.length > 1`
- **D-12:** Hovering over the badge shows a tooltip listing each worktree: branch name + shortened path (basename of directory)
- **D-13:** Primary worktree in the tooltip gets a subtle "main" label
- **D-14:** No click interaction needed — hover-only tooltip via Tailwind CSS (no JS state)
- **D-15:** Badge and tooltip styled consistent with VS Code dark theme (zinc color scale already in use)
- **D-16:** Phase 1 is full-stack: backend deduplication + API shape change + frontend badge/tooltip all ship together
- **D-17:** No change to how segments are structured — worktree info lives at `GroupPayload` level only

### Claude's Discretion

- Exact tooltip positioning and animation (fade, no-fade)
- Tailwind classes for badge colors
- Whether to show full path or just directory basename in tooltip (basename preferred for readability)
- How to handle the case where the same `.planning/` is found via multiple worktree paths during the scan pass (deduplication order)

### Deferred Ideas (OUT OF SCOPE)

- Showing which worktree's `.planning/` is newest/most recently modified — Phase 4 (Performance & Correctness)
- Clicking a worktree entry to open that directory in Explorer — out of scope (read-only app)
- Detecting stale worktrees (branch deleted on remote) — v2 backlog
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| WRKTR-01 | Project dropdown shows exactly one entry per canonical repo root (`.git` directory), regardless of how many worktrees exist | Canonical root resolution via `.git` file pointer; `by_repo` dict keyed on canonical path |
| WRKTR-02 | App detects git worktrees by checking if `.git` is a file (not a directory) and reads the `gitdir:` pointer to resolve the canonical repo root | `resolve_canonical_root()` helper pattern confirmed; `.git` file format documented |
| WRKTR-03 | Project entry in dropdown shows a badge with the count of active worktrees when more than one exists | `worktrees.length > 1` guard; Tailwind badge pattern confirmed |
| WRKTR-04 | Hovering or clicking the badge shows the list of worktree branch/directory names | `group` / `group-hover:visible` CSS-only tooltip; no JS state required |
| WRKTR-05 | An indicator marks which worktree is currently active (checked out) | `isPrimary: true` on main checkout (where `.git` is a directory); "main" label in tooltip |
</phase_requirements>

---

## Summary

This phase adds git worktree awareness to the project discovery pipeline so that a canonical repo with N linked worktrees checked out appears as exactly one entry in the project dropdown instead of N duplicate entries. All decisions are locked: detection via `.git` file check, resolution via `gitdir:` pointer, branch reading via pygit2, and a CSS-only hover tooltip badge on the frontend.

The backend changes are surgical: a `resolve_canonical_root()` helper is added (a pure function, easily testable), two lines in `discover_groups()` are changed to use the canonical key instead of the scanned path, `WorktreeInfo` dataclass is added to `project_discovery.py`, `ProjectGroup` gets a `worktrees` field, and `_group_to_json()` serializes it. Git service gets a `get_branch_name()` helper. The frontend changes are additive: `GroupPayload` gains `worktrees: WorktreeInfo[]`, and `ShellLayout.tsx` renders a conditional badge with a CSS group-hover tooltip adjacent to the repo dropdown.

The critical implementation subtlety is that worktree info must be **accumulated during the scan pass** (before the grouping loop) because multiple scan roots may each discover a different worktree of the same repo. The `by_repo` dict must accumulate a list of `(worktree_path, is_primary)` tuples per canonical key so the final `ProjectGroup` constructor has all worktrees available.

**Primary recommendation:** Implement `resolve_canonical_root()` as a standalone pure function in `project_discovery.py`, accumulate `(path, is_primary)` tuples in a parallel `by_repo_worktrees: dict[str, list[tuple[Path, bool]]]` during both scan passes, then build `WorktreeInfo` objects (with branch reading) in the grouping loop at the end of `discover_groups()`.

---

## Standard Stack

### Core (all already present in the project)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pygit2 | 1.19.2 (installed, verified) | Read branch shorthand from worktree path | Already used in `GitService`; `Repository.head.shorthand` confirmed working |
| pathlib | stdlib | Resolve `.git` file pointer path | `Path.is_file()` / `Path.read_text()` / `Path.resolve()` — no new deps |
| dataclasses | stdlib | `WorktreeInfo` dataclass | Existing `ProjectGroup` / `SegmentModel` use `@dataclass` — consistent |
| React 19 / Tailwind v4 | installed | Badge + tooltip rendering | `group` / `group-hover:` utilities available in Tailwind v4 |

### No New Dependencies Required

This phase requires zero new Python packages and zero new npm packages. All needed capabilities exist in the installed versions.

---

## Architecture Patterns

### Canonical Root Resolution Helper

A pure function added to `project_discovery.py` before the `ProjectDiscoveryService` class:

```python
# Source: git worktree specification + verified against pygit2 1.19.2
def _resolve_canonical_root(repo_dir: Path) -> Path:
    """Return canonical repo root for any directory (worktree or main checkout)."""
    dot_git = repo_dir / ".git"
    if dot_git.is_dir():
        return repo_dir  # already the canonical root
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
                # gitdir_path = /canonical/.git/worktrees/<name>
                # parent.parent = /canonical/.git  parent.parent.parent = /canonical
                canonical_root = gitdir_path.parent.parent.parent
                if canonical_root.is_dir():
                    return canonical_root
        except Exception:
            pass
    return repo_dir  # fallback: treat as its own root
```

**When to use:** Call at the beginning of both scan passes, before keying into `by_repo`.

### Worktree Accumulation Pattern

During both scan passes (GSD-2 and GSD-1), add a second parallel accumulator alongside `by_repo`:

```python
by_repo_worktrees: dict[str, list[tuple[Path, bool]]] = {}
# key = canonical root str, value = list of (worktree_path, is_primary)
```

In each scan pass, after resolving canonical root:

```python
canonical = _resolve_canonical_root(repo_dir)
canon_key = str(canonical)
is_primary = (repo_dir / ".git").is_dir()
wt_list = by_repo_worktrees.setdefault(canon_key, [])
if not any(str(p) == str(repo_dir) for p, _ in wt_list):
    wt_list.append((repo_dir, is_primary))
# Use canon_key (not str(repo_dir)) for by_repo
```

### WorktreeInfo Dataclass (backend)

Add to `project_discovery.py` alongside `ProjectGroup`:

```python
@dataclass
class WorktreeInfo:
    path: str
    branch: str
    is_primary: bool
```

Add to `ProjectGroup`:

```python
@dataclass
class ProjectGroup:
    # ... existing fields ...
    worktrees: list[WorktreeInfo] = field(default_factory=list)
```

### GitService.get_branch_name() Helper

Add alongside `get_latest_commit_date()` in `git_service.py`:

```python
def get_branch_name(self, repo_path: str) -> str:
    """Return the current branch shorthand, or short SHA if detached, or 'unknown'."""
    try:
        repo = pygit2.Repository(repo_path)
        if repo.head_is_detached:
            return str(repo.head.target)[:7]
        return repo.head.shorthand
    except Exception:
        return "unknown"
```

**Note:** `pygit2.Repository(path)` called directly with the worktree working directory works correctly — verified on pygit2 1.19.2. It does not require `pygit2.discover_repository()` first when passing the working directory path.

### Serialization in _group_to_json()

```python
def _group_to_json(g: ProjectGroup) -> dict[str, Any]:
    return {
        # ... existing keys ...
        "worktrees": [
            {
                "path": wt.path,
                "branch": wt.branch,
                "isPrimary": wt.is_primary,
            }
            for wt in g.worktrees
        ],
    }
```

### Frontend: GroupPayload Interface Extension

In `frontend/src/api.ts`, add `WorktreeInfo` interface and extend `GroupPayload`:

```typescript
export interface WorktreeInfo {
  path: string;
  branch: string;
  isPrimary: boolean;
}

export interface GroupPayload {
  // ... existing fields ...
  worktrees: WorktreeInfo[];
}
```

### Frontend: Badge + Tooltip in ShellLayout

The project dropdown is a `<select>` element. HTML `<option>` elements cannot contain arbitrary HTML. The badge must sit **outside the `<select>`**, adjacent to the dropdown label. The label + select + badge area can be wrapped in a `<div>` with relative positioning.

Tailwind v4 CSS-only hover tooltip pattern (no JS state — satisfies D-14):

```tsx
{/* In the group dropdown section, after the <select> */}
{activeGroup && activeGroup.worktrees.length > 1 && (
  <div className="group relative inline-block">
    <span className="cursor-default rounded bg-zinc-700 px-1.5 py-0.5 text-xs text-zinc-300">
      {activeGroup.worktrees.length} worktrees
    </span>
    <div className="invisible absolute left-0 top-full z-10 mt-1 w-64 rounded-md border border-zinc-700 bg-zinc-900 p-2 text-xs shadow-lg group-hover:visible">
      {activeGroup.worktrees.map((wt) => (
        <div key={wt.path} className="flex items-center gap-2 py-0.5">
          <span className="font-mono text-zinc-300">{wt.branch}</span>
          <span className="text-zinc-500">{wt.path.split(/[/\\]/).at(-1)}</span>
          {wt.isPrimary && (
            <span className="ml-auto text-zinc-600">main</span>
          )}
        </div>
      ))}
    </div>
  </div>
)}
```

**Positioning note:** The badge renders below the select label, not inside the `<select>`. The tooltip appears below the badge (`top-full`). This avoids any z-index conflict with the select dropdown.

### Anti-Patterns to Avoid

- **Keying `by_repo` by `str(repo_dir)` (scanned path):** The current bug. If three worktrees are scanned, three different keys are produced, three groups are created. Fix: always key by `str(canonical_root)`.
- **Building WorktreeInfo in the grouping loop without prior accumulation:** The grouping loop iterates `by_repo.items()` — at that point, only one segment is in each value (the last one won due to `by_repo[key] = [seg]` overwrite). Accumulation must happen during the scan pass.
- **Calling `pygit2.discover_repository()` before `pygit2.Repository()`:** Unnecessary. `pygit2.Repository(workdir_path)` handles worktree paths directly. The existing `GitService.get_latest_commit_date` uses `discover_repository` for a different reason (it may be passed a sub-path of the repo). For branch reading from the worktree root, direct `Repository(path)` is sufficient and cleaner.
- **Placing badge inside `<option>` elements:** Not possible in HTML. Badge must be outside the `<select>`.
- **Using `useState` for tooltip visibility:** D-14 explicitly mandates CSS-only hover via Tailwind `group-hover:`. No `useState` for this.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting linked worktrees | Custom git plumbing parser | `.git` file check (is_file) + `gitdir:` line read | git spec guarantees this format; no edge cases |
| Reading current branch | subprocess `git branch --show-current` | `pygit2.Repository.head.shorthand` | Already installed; no subprocess; handles detached HEAD cleanly |
| Worktree enumeration from canonical repo | `pygit2.repo.list_worktrees()` | Manual accumulation during scan | `list_worktrees()` only knows about registered worktrees from the PRIMARY repo's perspective; if we only scan a linked worktree path, we can't call `list_worktrees()` on it without first resolving the canonical repo — the accumulation approach is simpler and works regardless of scan order |
| CSS tooltip | React state + conditional render | Tailwind `group` / `group-hover:visible` | Zero JS, no re-renders, works in strict mode |

**Key insight on `list_worktrees()`:** pygit2 1.19.2 has `Repository.list_worktrees()` and `Repository.lookup_worktree()`. However this API is only useful when called on the canonical (primary) repo. If the scan discovers linked worktrees first, the canonical repo may not yet be in `by_repo`. The manual accumulation approach — collecting `(worktree_path, is_primary)` pairs during scan regardless of order — is more robust. The `list_worktrees()` API is better suited for a use case where we start from known canonical roots, which is not this app's model.

---

## Common Pitfalls

### Pitfall 1: GSD-2 scan uses `by_repo[key] = [seg]` (overwrites, not appends)

**What goes wrong:** The GSD-2 scan loop at `project_discovery.py` line 86 does `by_repo[key] = [seg]` — not `by_repo.setdefault(key, []).append(seg)`. If two worktrees both contain `.gsd/`, the second overwrites the first. After the canonical key fix, this will silently drop one worktree's segment.

**Why it happens:** Original code assumed one segment per repo-dir key (no deduplication). After the fix, multiple worktrees map to the same canonical key.

**How to avoid:** Change GSD-2 scan line to `by_repo.setdefault(canon_key, []).append(seg)`. For GSD-2, each worktree produces one segment; they should coexist under the same key so the user can still select them as segments. (Or: decide that GSD-2 deduplication keeps only one segment from the canonical root — this is Claude's discretion per the context notes about deduplication order.)

**Warning signs:** When testing with multiple worktrees, only one `.gsd/` worktree's data appears.

### Pitfall 2: `display_name` defaults to `rp.name` — after fix, `rp` is canonical root, which is correct

**What goes wrong:** After setting `root_path` to the canonical root string, `rp.name` gives the canonical directory's basename. For a linked worktree like `D:/repos/my-repo-feature`, the canonical root is `D:/repos/my-repo`, so `display_name = "my-repo"`. This is the desired behavior (D-04: `root_path` = canonical root). No fix needed.

**Warning signs:** None — this is correct behavior by design.

### Pitfall 3: `repo_dir.resolve()` vs path string comparison for deduplication guard

**What goes wrong:** On Windows, path strings may differ by case or trailing slash. Comparing `str(repo_dir) == str(other_dir)` without normalization can miss duplicates or create false matches.

**Why it happens:** `Path.resolve()` normalizes case on case-insensitive filesystems (Windows) but only when the path exists. If a scan root is specified with a different case than the actual directory, `str(Path(root).resolve())` handles this correctly — but both sides of the comparison must call `.resolve()` or canonicalize identically.

**How to avoid:** Use `Path(repo_dir).resolve()` for both the scan key and the comparison in the worktree accumulation guard. The existing code already uses `Path(root).resolve()` at the scan root level.

### Pitfall 4: `.git` file `gitdir:` path may use forward slashes on Windows

**What goes wrong:** On Windows, git writes `gitdir:` lines with forward slashes (`D:/repos/my-repo/.git/worktrees/feature`). `pathlib.Path()` on Windows handles forward slashes, but an explicit `Path(gitdir_str)` call must be made before checking `is_absolute()` — don't do string prefix detection for absolute paths (e.g., checking for `/` would miss `D:/` Windows paths).

**How to avoid:** Use `Path(gitdir_str).is_absolute()` for the absolute-vs-relative check, not string manipulation. Verified: `pathlib.Path('D:/foo/bar').is_absolute()` returns `True` on Windows.

### Pitfall 5: Branch read during scan (I/O in the scan loop)

**What goes wrong:** `get_branch_name()` opens a `pygit2.Repository` for every worktree discovered. This is disk I/O inside the scan loop. For a scan root with 100 repos, this adds 100 `Repository()` calls on top of existing discovery work.

**Why it happens:** Branch reading is inherently tied to opening the repo.

**How to avoid:** Branch reading is deferred to the grouping loop (after scan), not inside the inner scan loop. Collect `(path, is_primary)` during scan; call `get_branch_name()` only once per unique worktree path during `ProjectGroup` construction. This is already N calls total (where N = total worktrees across all repos), same as before.

### Pitfall 6: `ShellLayout.tsx` `activeGroup` is already computed but `worktrees` field did not exist before

**What goes wrong:** `activeGroup` is derived via `useMemo` in `ShellLayout`. If `GroupPayload` is updated to include `worktrees` but the API still returns the old shape (e.g., during a hot-reload dev session), `worktrees` will be `undefined` causing a runtime error on `.length`.

**How to avoid:** Guard with `activeGroup.worktrees?.length > 1` or initialize `worktrees` with a default in the `GroupPayload` interface. Since this is a full-stack change shipping together, in practice both layers update atomically — but defensive coding with `??` is cheap.

---

## Code Examples

### Complete `_resolve_canonical_root` function

```python
# Source: git worktree file format specification (gitrepository-layout manpage)
# Verified: pathlib handles forward-slash absolute paths on Windows correctly
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
                # parent = .git/worktrees, parent.parent = .git, parent.parent.parent = canonical
                canonical = gitdir_path.parent.parent.parent
                if canonical.is_dir():
                    return canonical
        except Exception:
            pass
    return repo_dir
```

### `get_branch_name` in GitService

```python
# Source: pygit2 1.19.2 — Repository.head.shorthand confirmed str type, works on worktree paths
def get_branch_name(self, repo_path: str) -> str:
    """Return current branch shorthand. Falls back to short SHA (detached) or 'unknown'."""
    if not repo_path:
        return "unknown"
    try:
        repo = pygit2.Repository(repo_path)
        if repo.head_is_detached:
            return str(repo.head.target)[:7]
        return repo.head.shorthand
    except Exception:
        return "unknown"
```

### Modified scan pass (GSD-2 example)

```python
# In discover_groups(), before the grouping loop:
by_repo_worktrees: dict[str, list[tuple[Path, bool]]] = {}

# Inside the GSD-2 scan loop (replaces lines 82-87):
repo_dir = gsd_dir.parent
canonical = _resolve_canonical_root(repo_dir)
canon_key = str(canonical)
is_primary = (repo_dir / ".git").is_dir()
seg = self._discover_gsd2(repo_dir, gsd_dir)
if seg:
    by_repo.setdefault(canon_key, []).append(seg)
    gsd2_repos.add(canon_key)
    wt_entry = (repo_dir, is_primary)
    if not any(str(p) == str(repo_dir) for p, _ in by_repo_worktrees.get(canon_key, [])):
        by_repo_worktrees.setdefault(canon_key, []).append(wt_entry)
```

### WorktreeInfo construction in the grouping loop

```python
# In the grouping loop, before ProjectGroup construction:
wt_tuples = by_repo_worktrees.get(repo_key, [(rp, True)])
worktrees = [
    WorktreeInfo(
        path=str(wt_path),
        branch=self._git.get_branch_name(str(wt_path)),
        is_primary=wt_is_primary,
    )
    for wt_path, wt_is_primary in wt_tuples
]
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Detect worktrees via `git worktree list` subprocess | `.git` file check (pure Python, no subprocess) | This phase | No git CLI required; faster; no shell injection risk |
| Group keyed by scanned path | Group keyed by canonical root | This phase | Deduplication works regardless of how many worktrees are checked out |

**Deprecated/outdated:**
- pygit2 `Repository.list_worktrees()`: Available but not used here — only works from primary repo perspective. The accumulation approach is simpler.

---

## Open Questions

1. **Multiple worktrees with separate `.planning/` dirs**
   - What we know: Each worktree checkout is a separate directory. If the repo has `.planning/` at root, each worktree has its own copy of those files at `worktree_path/.planning/`. If the user has n worktrees, the scan may find n identical-path `.planning/` dirs (relative to each worktree root). After canonical key deduplication, only one set of segments is stored — from whichever worktree's data was processed last (GSD-1 uses `by_repo.setdefault(key, []).append(seg)` — all segments accumulate).
   - What's unclear: Should all worktrees' segments be included, or only the canonical root's? The CONTEXT.md says "All worktree paths that resolve to the same canonical root become a single `ProjectGroup`" (D-03), and segments live at the group level (D-17). Multiple segments from multiple worktrees of the same repo is probably undesirable — the user would see duplicate workstream/project selectors.
   - Recommendation: In the GSD-1 scan, if `canon_key` already has segments, skip adding more segments from other worktrees of the same repo. The canonical root's data is authoritative. This is "deduplication order" — Claude's discretion per CONTEXT.md.

2. **`display_name` when canonical root and worktree have different basenames**
   - What we know: `display_name = rp.name` where `rp = Path(repo_key)` = canonical root. If canonical root is `my-repo` and a worktree is `my-repo-feature`, the display name is `my-repo`. Correct.
   - What's unclear: No gap — behavior is correct by design.

3. **Worktrees list ordering in tooltip**
   - What we know: The tooltip lists worktrees by iteration order of `by_repo_worktrees[key]`.
   - Recommendation: Sort primary first, then alphabetical by basename. Simple `sorted(wts, key=lambda x: (not x.is_primary, x.path))`.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| pygit2 | `get_branch_name()` | ✓ | 1.19.2 (verified) | Use `"unknown"` (D-10 handles this) |
| pathlib | `_resolve_canonical_root()` | ✓ | stdlib | — |
| Python 3.11+ | All backend | ✓ | (project constraint) | — |
| Node.js / npm | Frontend build | ✓ | (present in project) | — |

**No missing dependencies.** This phase requires no new installs.

---

## Project Constraints (from CLAUDE.md)

- **No stack changes:** Python 3.11+ / FastAPI / pywebview / React 19 / Tailwind CSS v4 / Vite 6 — all respected; zero new dependencies
- **Read-only app:** No writes to project files — worktree detection reads `.git` file only
- **Settings path compatibility:** `%LOCALAPPDATA%\WinGSDMonitor\settings.json` PascalCase — unaffected by this phase
- **Naming:** New dataclass `WorktreeInfo` (PascalCase), method `get_branch_name` (snake_case), helper `_resolve_canonical_root` (snake_case with leading underscore = module-level private) — all compliant
- **Type hints:** All new functions must have full return type annotations; `from __future__ import annotations` already at top of relevant modules
- **Pydantic models:** `WorktreeInfo` is a `@dataclass` (consistent with `ProjectGroup`/`SegmentModel`), not a Pydantic model — consistent with existing API layer pattern
- **React patterns:** Named export for any new component; `type` keyword for interface imports; no `any` in interface definitions
- **Tailwind:** Dark theme using `zinc` color scale; no custom CSS classes beyond `src/index.css`
- **GSD Workflow Enforcement:** Changes should go through a GSD command (`/gsd:execute-phase`) — do not make direct repo edits outside a GSD workflow

---

## Sources

### Primary (HIGH confidence)
- pygit2 1.19.2 — verified live: `Repository.head.shorthand`, `head_is_detached`, `list_worktrees()`, `Worktree` class attributes — all confirmed by direct Python invocation
- pathlib stdlib — `Path.is_file()`, `Path.is_dir()`, `Path.read_text()`, `Path.resolve()`, `Path.is_absolute()` — verified behavior on Windows for forward-slash paths
- `gsd_monitor/services/project_discovery.py` — current `discover_groups()` implementation read directly; insertion points identified at lines 82–87 (GSD-2) and 94–108 (GSD-1)
- `gsd_monitor/services/git_service.py` — current `GitService` read directly; `get_branch_name()` placement confirmed
- `gsd_monitor/api/app.py` — `_group_to_json()` and `ProjectGroup` import; `worktrees` key addition point confirmed
- `frontend/src/api.ts` — `GroupPayload` interface read directly; `WorktreeInfo` addition point confirmed
- `frontend/src/ShellLayout.tsx` — dropdown render loop at lines 59–79 read directly; badge placement after `<select>` confirmed
- git worktree file format (gitrepository-layout): `.git` file in linked worktree = `gitdir: <path>`, where path ends in `.git/worktrees/<name>` — standard git behavior

### Secondary (MEDIUM confidence)
- Tailwind CSS v4 `group` / `group-hover:visible` pattern — verified via Tailwind v4 utilities (group modifier is a first-class feature unchanged from v3)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries present and version-verified
- Architecture: HIGH — insertion points read directly from source; algorithm verified with live Python
- Pitfalls: HIGH — identified from reading actual code paths in `project_discovery.py` and `ShellLayout.tsx`

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable domain; pygit2 API is stable)
