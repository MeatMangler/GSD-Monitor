import { NavLink } from "react-router-dom";
import { useMemo, useState, useEffect, useRef, type ReactNode } from "react";
import { useApp } from "./context";
import type { GroupPayload, SegmentPayload, WorktreeInfo } from "./api";
import gsdIcon from "./assets/gsd-icon.png";

const nav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/docs",      label: "Docs" },
  { to: "/artifacts", label: "Artifacts" },
  { to: "/drift",     label: "Drift" },
  { to: "/quick-tasks", label: "Quick Tasks" },
  { to: "/verification", label: "Verification" },
  { to: "/insights",  label: "Insights" },
  { to: "/settings",  label: "Settings" },
  { to: "/logs",      label: "Logs" },
];

export function ShellLayout({ children }: { children: ReactNode }) {
  const {
    groups,
    loading,
    error,
    forceRefresh,
    selectedGroupId,
    setSelectedGroupId,
    selectedSegmentKey,
    setSelectedSegmentKey,
  } = useApp();

  const [lastScanned, setLastScanned] = useState<string | null>(null);
  useEffect(() => {
    if (!loading) setLastScanned(new Date().toLocaleTimeString());
  }, [loading]);

  const [navCollapsed, setNavCollapsed] = useState(false);
  const [navWidth, setNavWidth] = useState(288);
  const [navResizing, setNavResizing] = useState(false);
  const [navDragHover, setNavDragHover] = useState(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(0);

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
    <div
      className="flex h-screen overflow-hidden bg-[#1e1e1e]"
      style={{ userSelect: navResizing ? "none" : undefined }}
    >
      {/* ── Main nav sidebar ── */}
      <aside
        className="shrink-0 flex flex-col border-r border-[#474747] bg-[#252526] overflow-hidden"
        style={{ width: navCollapsed ? "48px" : `${navWidth}px` }}
      >
        {/* Header */}
        <div className="shrink-0 border-b border-[#474747] p-3">
          {navCollapsed ? (
            <div className="flex flex-col items-center gap-2">
              <img
                src={gsdIcon}
                alt="GSD"
                width={28}
                height={28}
                style={{ objectFit: "contain", borderRadius: "5px" }}
              />
              <button
                type="button"
                title="Expand sidebar"
                onClick={() => setNavCollapsed(false)}
                className="text-[#858585] hover:text-[#cccccc] hover:bg-[#2a2d2e] rounded p-0.5 text-base leading-none w-full flex items-center justify-center"
              >
                ›
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between gap-2 w-full">
              <div className="flex items-center gap-2 min-w-0">
                <img
                  src={gsdIcon}
                  alt="GSD"
                  width={32}
                  height={32}
                  style={{ objectFit: "contain", borderRadius: "6px", flexShrink: 0 }}
                />
                <div className="min-w-0">
                  <h1 className="text-sm font-semibold tracking-tight text-[#cccccc] truncate">GSD Monitor</h1>
                  <p className="mt-0.5 text-xs text-[#858585] truncate">Grouped project roots</p>
                </div>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <button
                  type="button"
                  title={lastScanned ? `Force rescan — last scanned ${lastScanned}` : "Force rescan"}
                  disabled={loading}
                  onClick={() => void forceRefresh()}
                  className="rounded p-1 text-[#858585] hover:text-[#cccccc] hover:bg-[#2a2d2e] disabled:opacity-40"
                >
                  ↻
                </button>
                <button
                  type="button"
                  title="Collapse sidebar"
                  onClick={() => setNavCollapsed(true)}
                  className="rounded p-1 text-[#858585] hover:text-[#cccccc] hover:bg-[#2a2d2e] text-base leading-none"
                >
                  ‹
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Project / workstream selectors — hidden when collapsed */}
        {!navCollapsed && (
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
                      {wt.isPrimary && <span className="ml-auto text-[#858585]">main</span>}
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
                    <option key={p} value={p}>{p}</option>
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
                    <option key={w} value={w}>{w}</option>
                  ))}
                </select>
              </>
            )}
          </div>
        )}

        {/* Nav links */}
        <nav className="mt-auto flex flex-col gap-0.5 p-2">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              title={navCollapsed ? item.label : undefined}
              className={({ isActive }) =>
                `rounded-md px-3 py-2 text-sm font-medium ${
                  isActive ? "bg-[#2a2d2e] text-[#cccccc]" : "text-[#858585] hover:bg-[#2a2d2e] hover:text-[#cccccc]"
                } ${navCollapsed ? "flex items-center justify-center" : ""}`
              }
            >
              {navCollapsed ? item.label[0] : item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Drag-to-resize handle — only when expanded */}
      {!navCollapsed && (
        <div
          className="w-1.5 shrink-0 cursor-col-resize select-none"
          style={{ background: navResizing || navDragHover ? "#007acc" : "#2a2d2e" }}
          title="Drag to resize"
          onPointerEnter={() => setNavDragHover(true)}
          onPointerLeave={() => setNavDragHover(false)}
          onPointerDown={(e) => {
            e.currentTarget.setPointerCapture(e.pointerId);
            dragStartX.current = e.clientX;
            dragStartWidth.current = navWidth;
            setNavResizing(true);
          }}
          onPointerMove={(e) => {
            if (!e.currentTarget.hasPointerCapture(e.pointerId)) return;
            const delta = e.clientX - dragStartX.current;
            setNavWidth(Math.min(480, Math.max(160, dragStartWidth.current + delta)));
          }}
          onPointerUp={(e) => {
            e.currentTarget.releasePointerCapture(e.pointerId);
            setNavDragHover(false);
            setNavResizing(false);
          }}
        />
      )}

      <main className="min-w-0 flex-1 overflow-auto">{children}</main>
    </div>
  );
}
