import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useApp } from "../context";
import { Drawer } from "../Drawer";
import { byLastUpdated, fmtDate, statusLabel, statusBorderClass } from "../utils";

export function DashboardPage() {
  const { activeProject, activeSegment, groups, loading } = useApp();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedNumber, setSelectedNumber] = useState<number | null>(null);

  const phases = useMemo(
    () =>
      activeProject?.milestones
        .flatMap((m) => m.phases.map((p) => ({ ...p, milestoneTitle: m.title })))
        .sort(byLastUpdated) ?? [],
    [activeProject],
  );

  const selected = useMemo(
    () => (selectedNumber !== null ? (phases.find((p) => p.number === selectedNumber) ?? null) : null),
    [phases, selectedNumber],
  );

  const stats = useMemo(() => {
    if (!activeProject) return null;
    const phases = activeProject.milestones.flatMap((m) => m.phases);
    const total = phases.length;
    const complete = phases.filter((p) => p.status === "complete").length;
    const completion = total ? Math.round((complete / total) * 100) : 0;
    const phasesDone = complete;
    const phasesTotal = total;
    const activePhaseName =
      activeSegment?.stateCurrentPosition ??
      phases.find((p) => p.status === "in_progress")?.title ??
      "—";
    let driftLabel = "No drift";
    const hasM = phases.some((p) => p.drift === "major");
    const hasN = phases.some((p) => p.drift === "minor");
    if (hasM) driftLabel = "Major drift";
    else if (hasN) driftLabel = "Minor drift";
    return { completion, phasesDone, phasesTotal, activePhaseName, driftLabel, gsdVersion: activeProject.version };
  }, [activeProject, activeSegment]);

  const breadcrumb = useMemo(() => {
    const activeGroup = groups.find((g) => g.id === activeSegment?.groupId) ?? null;
    const groupName = activeGroup?.displayName ?? "—";
    const projectName = activeProject?.name ?? "—";
    const phases = activeProject?.milestones.flatMap((m) => m.phases) ?? [];
    const activePhaseTitle =
      activeSegment?.stateCurrentPosition ??
      phases.find((p) => p.status === "in_progress")?.title ??
      [...phases].filter((p) => p.status === "complete").sort(byLastUpdated)[0]?.title ??
      "—";
    return { groupName, projectName, activePhaseTitle };
  }, [activeProject, activeSegment, groups]);

  if (loading) return <div className="p-8 text-[#858585]">Loading…</div>;
  if (!activeProject)
    return (
      <div className="p-8 text-[#858585]">
        Add scan roots in Settings and select a project.
      </div>
    );

  return (
    <div className="p-6">
      {/* Breadcrumb — per D-09, D-10, D-11 */}
      <div className="mb-4 flex items-center gap-1 py-2 text-sm font-semibold">
        <span className="text-[#858585]">{breadcrumb.groupName}</span>
        <span className="mx-1 text-[#474747]">/</span>
        <span className="text-[#858585]">{breadcrumb.projectName}</span>
        <span className="mx-1 text-[#474747]">/</span>
        <span className="max-w-[240px] truncate text-[#cccccc]">{breadcrumb.activePhaseTitle}</span>
      </div>

      {/* Stats bar — per D-01 through D-05 */}
      <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
        {/* Card 1: Completion % (D-01, unchanged content) */}
        <div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
          <div className="text-2xl font-semibold text-[#cccccc]">{stats?.completion ?? 0}%</div>
          <div className="text-xs text-[#858585]">Completion</div>
        </div>
        {/* Card 2: Phases done/total (D-02) */}
        <div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
          <div className="text-2xl font-semibold text-[#cccccc]">
            {stats?.phasesDone ?? 0} / {stats?.phasesTotal ?? 0}
          </div>
          <div className="text-xs text-[#858585]">Phases done</div>
        </div>
        {/* Card 3: Active phase name (D-03) — text-sm not text-2xl since it's a string */}
        <div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
          <div className="text-sm font-semibold text-[#cccccc] truncate">
            {stats?.activePhaseName ?? "—"}
          </div>
          <div className="text-xs text-[#858585]">Active phase</div>
        </div>
        {/* Card 4: Drift label (D-04, unchanged content) */}
        <div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
          <div className="text-sm font-semibold text-[#cccccc]">{stats?.driftLabel}</div>
          <div className="text-xs text-[#858585]">Drift</div>
        </div>
      </div>

      {/* GSD version badge — keep existing, update colors */}
      <div className="mb-4 flex items-center gap-2">
        <span className="rounded bg-[#007acc]/30 px-2 py-0.5 text-xs font-medium text-[#cccccc]">
          {stats?.gsdVersion === "gsd2" ? "GSD-2" : "GSD-1"}
        </span>
      </div>

      {/* Phase list — per D-06, D-07, D-08 */}
      <div className="space-y-2">
        {phases.map((p) => (
          <button
            type="button"
            key={`${p.number}-${p.title}`}
            className={`w-full rounded-md border border-[#474747] border-l-[3px] ${statusBorderClass(p.status)} bg-[#1e1e1e] p-4 text-left transition-colors hover:bg-[#2a2d2e]`}
            onClick={() => {
              setSelectedNumber(p.number);
              setDrawerOpen(true);
            }}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="font-mono font-medium text-[#cccccc]">
                {String(p.number).padStart(2, "0")} — {p.title}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#858585]">{statusLabel(p.status)}</span>
                <span className="text-xs text-[#858585]">{fmtDate(p.last_updated)}</span>
              </div>
            </div>
            {p.goal && <p className="mt-1 line-clamp-2 text-xs text-[#858585]">{p.goal}</p>}
          </button>
        ))}
      </div>

      {/* Drawer — unchanged per D-08 */}
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={selected ? `${String(selected.number).padStart(2, "0")} — ${selected.title}` : "Phase"}
      >
        {selected && (
          <div className="space-y-4">
            {selected.plan_content && (
              <div>
                <h3 className="mb-1 text-xs font-semibold uppercase text-[#858585]">Plan</h3>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{selected.plan_content}</ReactMarkdown>
                </div>
              </div>
            )}
            {selected.research_content && (
              <div>
                <h3 className="mb-1 text-xs font-semibold uppercase text-[#858585]">Research</h3>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{selected.research_content}</ReactMarkdown>
                </div>
              </div>
            )}
            {selected.validation_content && (
              <div>
                <h3 className="mb-1 text-xs font-semibold uppercase text-[#858585]">Validation</h3>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{selected.validation_content}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
}
