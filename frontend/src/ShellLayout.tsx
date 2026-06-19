import { NavLink } from "react-router-dom";
import { useMemo, type ReactNode } from "react";
import { useApp } from "./context";
import type { GroupPayload, SegmentPayload, WorktreeInfo } from "./api";

const nav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/docs", label: "Docs" },
  { to: "/drift", label: "Drift" },
  { to: "/quick-tasks", label: "Quick Tasks" },
  { to: "/verification", label: "Verification" },
  { to: "/insights", label: "Insights" },
  { to: "/settings", label: "Settings" },
];

export function ShellLayout({ children }: { children: ReactNode }) {
  const {
    groups,
    loading,
    error,
    selectedGroupId,
    setSelectedGroupId,
    selectedSegmentKey,
    setSelectedSegmentKey,
  } = useApp();

  const activeGroup = useMemo(
    (): GroupPayload | null => groups.find((g) => g.id === selectedGroupId) ?? null,
    [groups, selectedGroupId],
  );

  const gsdProjects = useMemo((): string[] => {
    if (!activeGroup) return [];
    const set = new Set<string>();
    for (const s of activeGroup.segments) {
      if (s.gsdProject) set.add(s.gsdProject);
    }
    return [...set];
  }, [activeGroup]);

  const workstreams = useMemo((): string[] => {
    if (!activeGroup) return [];
    const set = new Set<string>();
    for (const s of activeGroup.segments) {
      if (s.workstream) set.add(s.workstream);
    }
    return [...set];
  }, [activeGroup]);

  return (
    <div className="flex h-screen overflow-hidden bg-[#1e1e1e]">
      <aside className="flex w-72 shrink-0 flex-col border-r border-[#474747] bg-[#252526]">
        <div className="border-b border-[#474747] p-3">
          <div className="flex items-center gap-2">
            <img src="/gsd-icon.png" alt="GSD" className="h-8 w-8 rounded-md shrink-0 object-contain" />
            <div>
              <h1 className="text-sm font-semibold tracking-tight text-[#cccccc]">GSD Monitor</h1>
              <p className="mt-0.5 text-xs text-[#858585]">Grouped project roots</p>
            </div>
          </div>
        </div>
        <div className="space-y-2 p-3">
          {loading && <p className="text-xs text-[#858585]">Loading…</p>}
          {error && <p className="text-xs text-red-400">{error}</p>}
          <label className="block text-xs font-medium text-[#858585]">Workspace / repo</label>
          <select
            className="w-full rounded-md border border-[#474747] bg-[#252526] px-2 py-1.5 text-sm text-[#cccccc]"
            value={selectedGroupId ?? ""}
            onChange={(e) => {
              setSelectedGroupId(e.target.value || null);
              const g = groups.find((x: GroupPayload) => x.id === e.target.value);
              if (g?.segments.length) {
                const d =
                  g.segments.find((s: SegmentPayload) => s.segmentKey === g.defaultSegmentKey) ??
                  g.segments[0];
                setSelectedSegmentKey(d.segmentKey);
              }
            }}
          >
            {groups.map((g) => (
              <option key={g.id} value={g.id}>
                {g.displayName}
                {g.isWorkspace ? " (workspace)" : ""}
              </option>
            ))}
          </select>
          {activeGroup && (activeGroup.worktrees?.length ?? 0) > 1 && (
            <div className="group relative inline-block">
              <span className="cursor-default rounded bg-[#2a2d2e] px-1.5 py-0.5 text-xs text-[#858585]">
                {activeGroup.worktrees.length} worktrees
              </span>
              <div className="invisible absolute left-0 top-full z-10 mt-1 w-64 rounded-md border border-[#474747] bg-[#252526] p-2 text-xs shadow-lg group-hover:visible">
                {activeGroup.worktrees.map((wt: WorktreeInfo) => (
                  <div key={wt.path} className="flex items-center gap-2 py-0.5">
                    <span className="font-mono text-[#cccccc]">{wt.branch}</span>
                    <span className="text-[#858585]">{wt.path.split(/[/\\]/).at(-1)}</span>
                    {wt.isPrimary && (
                      <span className="ml-auto text-[#858585]">main</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          {gsdProjects.length > 0 && (
            <>
              <label className="block text-xs font-medium text-[#858585]">GSD project</label>
              <select
                className="w-full rounded-md border border-[#474747] bg-[#252526] px-2 py-1.5 text-sm text-[#cccccc]"
                value={
                  activeGroup?.segments.find((s: SegmentPayload) => s.segmentKey === selectedSegmentKey)
                    ?.gsdProject ?? ""
                }
                onChange={(e) => {
                  const proj = e.target.value || null;
                  const cur = activeGroup?.segments.find(
                    (s: SegmentPayload) => s.segmentKey === selectedSegmentKey,
                  );
                  const seg = activeGroup?.segments.find((s: SegmentPayload) => {
                    if (s.gsdProject !== proj) return false;
                    if (workstreams.length === 0) return true;
                    return s.workstream === cur?.workstream;
                  });
                  if (seg) setSelectedSegmentKey(seg.segmentKey);
                }}
              >
                <option value="">(flat / default)</option>
                {gsdProjects.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </>
          )}
          {workstreams.length > 0 && (
            <>
              <label className="block text-xs font-medium text-[#858585]">Workstream</label>
              <select
                className="w-full rounded-md border border-[#474747] bg-[#252526] px-2 py-1.5 text-sm text-[#cccccc]"
                value={
                  activeGroup?.segments.find((s: SegmentPayload) => s.segmentKey === selectedSegmentKey)
                    ?.workstream ?? ""
                }
                onChange={(e) => {
                  const ws = e.target.value || null;
                  const cur = activeGroup?.segments.find(
                    (s: SegmentPayload) => s.segmentKey === selectedSegmentKey,
                  );
                  const seg = activeGroup?.segments.find(
                    (s: SegmentPayload) =>
                      s.workstream === ws &&
                      s.gsdProject === cur?.gsdProject &&
                      s.gsdVersion === cur?.gsdVersion,
                  );
                  if (seg) setSelectedSegmentKey(seg.segmentKey);
                }}
              >
                <option value="">—</option>
                {workstreams.map((w) => (
                  <option key={w} value={w}>
                    {w}
                  </option>
                ))}
              </select>
            </>
          )}
        </div>
        <nav className="mt-auto flex flex-col gap-0.5 p-2">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-md px-3 py-2 text-sm font-medium ${isActive ? "bg-[#2a2d2e] text-[#cccccc]" : "text-[#858585] hover:bg-[#2a2d2e] hover:text-[#cccccc]"}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="min-w-0 flex-1 overflow-auto">{children}</main>
    </div>
  );
}
