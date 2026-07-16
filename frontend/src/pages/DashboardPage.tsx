import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
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
    const total = phases.length;
    const complete = phases.filter((p) => p.status === "complete").length;
    const completion = total ? Math.round((complete / total) * 100) : 0;
    const phasesDone = complete;
    const phasesTotal = total;
    const activePhaseName =
      activeSegment?.stateCurrentPosition ??
      phases.find((p) => p.status === "in_progress")?.title ??
      null;
    // If nothing is in_progress, surface the most recently updated planned phase
    // that already has plan docs written — this covers the "about to execute" state.
    const nextUpName =
      activePhaseName === null
        ? (phases.find((p) => p.status === "not_started" && p.has_plan)?.title ?? null)
        : null;
    let driftLabel = "No drift";
    const hasM = phases.some((p) => p.drift === "major");
    const hasN = phases.some((p) => p.drift === "minor");
    if (hasM) driftLabel = "Major drift";
    else if (hasN) driftLabel = "Minor drift";
    return { completion, phasesDone, phasesTotal, activePhaseName, nextUpName, driftLabel, gsdVersion: activeProject.version };
  }, [activeProject, activeSegment, phases]);

  const breadcrumb = useMemo(() => {
    const activeGroup = groups.find((g) => g.id === activeSegment?.groupId) ?? null;
    const groupName = activeGroup?.displayName ?? "—";
    const projectName = activeProject?.name ?? "—";
    const activePhaseTitle =
      activeSegment?.stateCurrentPosition ??
      phases.find((p) => p.status === "in_progress")?.title ??
      phases.find((p) => p.status === "not_started" && p.has_plan)?.title ??
      [...phases].filter((p) => p.status === "complete").sort(byLastUpdated)[0]?.title ??
      "—";
    return { groupName, projectName, activePhaseTitle };
  }, [activeProject, activeSegment, groups, phases]);

  // Progress data — from STATE.md-sourced fields on activeProject (per PROG-02, D-08)
  const progressData = useMemo(() => {
    if (!activeProject) return null;
    const { progress_percent, completed_phases, total_phases } = activeProject;
    if (
      progress_percent === undefined ||
      completed_phases === undefined ||
      total_phases === undefined ||
      total_phases === 0
    ) {
      return null;
    }
    return { progress_percent, completed_phases, total_phases };
  }, [activeProject]);

  if (loading) return <div className="p-8 text-[#858585]">Loading…</div>;
  if (!activeProject)
    return (
      <div className="p-8 text-[#858585]">
        Add scan roots in Settings and select a project.
      </div>
    );

  const handoffInfo = activeProject.handoff_info;
  const isPaused = handoffInfo?.paused === true;
  const configInfo = activeProject.config_info;

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

      {/* Pause banner — per DOCS-06, D-06, UI-SPEC section 2 */}
      {isPaused && handoffInfo && (
        <div className="mb-4 rounded-md border border-amber-800/40 bg-amber-900/20 px-4 py-2 flex items-center justify-between">
          <span className="flex items-center">
            <span className="inline-block w-1 h-1 rounded-full bg-amber-400 mr-2" />
            <span className="text-xs font-semibold text-amber-400">Paused</span>
          </span>
          <span className="text-xs text-[#858585]">
            Phase {handoffInfo.phase}, Plan {handoffInfo.plan}
            {" · paused "}
            {handoffInfo.timestamp ? fmtDate(handoffInfo.timestamp) : ""}
          </span>
        </div>
      )}

      {/* Resume context banner — per DOCS-07 */}
      {activeProject.continue_here && (
        <div className="mb-4 rounded-md border border-sky-800/40 bg-sky-900/20 px-4 py-2 flex items-center">
          <span className="inline-block w-1 h-1 rounded-full bg-sky-400 mr-2" />
          <span className="text-xs font-semibold text-sky-400">Resume context available</span>
          <span className="ml-2 text-xs text-[#858585]">.continue-here.md</span>
        </div>
      )}

      {/* Stats bar — per D-01 through D-05 */}
      <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
        {/* Card 1: Completion % (D-01) with compact progress bar (PROG-02, UI-SPEC section 1) */}
        <div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
          <div className="text-2xl font-semibold text-[#cccccc]">{stats?.completion ?? 0}%</div>
          <div className="text-xs text-[#858585]">Completion</div>
          {progressData && (
            <div className="mt-2 w-full h-1 rounded-full bg-[#474747]">
              <div
                className="h-1 rounded-full bg-[#4ec994]"
                style={{ width: `${progressData.progress_percent}%` }}
              />
            </div>
          )}
        </div>
        {/* Card 2: Phases done/total (D-02) */}
        <div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
          <div className="text-2xl font-semibold text-[#cccccc]">
            {stats?.phasesDone ?? 0} / {stats?.phasesTotal ?? 0}
          </div>
          <div className="text-xs text-[#858585]">Phases done</div>
        </div>
        {/* Card 3: Active phase / next-up phase (D-03) */}
        <div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
          <div className="text-sm font-semibold text-[#cccccc] truncate">
            {stats?.activePhaseName ?? stats?.nextUpName ?? "—"}
          </div>
          <div className="text-xs text-[#858585]">
            {stats?.activePhaseName == null && stats?.nextUpName != null ? "Next up" : "Active phase"}
          </div>
        </div>
        {/* Card 4: Drift label (D-04, unchanged content) */}
        <div className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-center">
          <div className="text-sm font-semibold text-[#cccccc]">{stats?.driftLabel}</div>
          <div className="text-xs text-[#858585]">Drift</div>
        </div>
      </div>

      {/* Detail progress bar — per PROG-02, UI-SPEC section 1 */}
      {progressData && (
        <div className="mb-4">
          <div className="mb-1 text-xs text-[#858585]">
            {progressData.completed_phases} of {progressData.total_phases} phases complete
            {" "}
            <span className="text-[#cccccc]">{progressData.progress_percent}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-[#474747]">
            <div
              className="h-2 rounded-full bg-[#4ec994]"
              style={{ width: `${progressData.progress_percent}%` }}
            />
          </div>
        </div>
      )}

      {/* GSD version badge — per DETECT-01, UI-SPEC section 6 */}
      <div className="mb-4 flex items-center gap-2">
        {stats?.gsdVersion === "gsd-core" ? (
          <span className="rounded bg-[#007acc]/30 px-2 py-0.5 text-xs font-medium text-[#cccccc]">
            gsd-core
          </span>
        ) : (
          <span className="rounded bg-[#2a2d2e] px-2 py-0.5 text-xs font-medium text-[#858585]">
            GSD-1
          </span>
        )}
      </div>

      {/* Config badge row — per DOCS-08, D-07, UI-SPEC section 3 */}
      {configInfo && (
        <div className="mb-4 flex items-center gap-2">
          {configInfo.workflow_mode && (
            <span className="rounded bg-[#2a2d2e] px-1.5 py-0.5 text-xs text-[#858585]">
              {configInfo.workflow_mode}
            </span>
          )}
          {configInfo.model_profile && (
            <span className="rounded bg-[#2a2d2e] px-1.5 py-0.5 text-xs text-[#858585]">
              {configInfo.model_profile}
            </span>
          )}
          {configInfo.branching_strategy && (
            <span className="rounded bg-[#2a2d2e] px-1.5 py-0.5 text-xs text-[#858585]">
              {configInfo.branching_strategy}
            </span>
          )}
        </div>
      )}

      {/* Phase list — per D-06, D-07, D-08 */}
      <div className="space-y-2">
        {phases.map((p) => {
          const phaseId = p.code ? p.code : String(p.number).padStart(2, "0");
          return (
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
                  {phaseId} — {p.title}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#858585]">{statusLabel(p.status)}</span>
                  <span className="text-xs text-[#858585]">{fmtDate(p.last_updated)}</span>
                </div>
              </div>
              {p.goal && <p className="mt-1 line-clamp-2 text-xs text-[#858585]">{p.goal}</p>}
            </button>
          );
        })}
      </div>

      {/* Drawer — per D-08, UI-SPEC section 5 */}
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={selected ? `${selected.code ? selected.code : String(selected.number).padStart(2, "0")} — ${selected.title}` : "Phase"}
      >
        {selected && (
          <div className="space-y-4">
            {selected.plan_content && (
              <div>
                <h3 className="mb-1 text-xs font-semibold uppercase text-[#858585]">Plan</h3>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>{selected.plan_content}</ReactMarkdown>
                </div>
              </div>
            )}
            {selected.research_content && (
              <div>
                <h3 className="mb-1 text-xs font-semibold uppercase text-[#858585]">Research</h3>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>{selected.research_content}</ReactMarkdown>
                </div>
              </div>
            )}
            {selected.validation_content && (
              <div>
                <h3 className="mb-1 text-xs font-semibold uppercase text-[#858585]">Validation</h3>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>{selected.validation_content}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
}
