import { useEffect, useMemo, useState } from "react";
import { useApp } from "../context";
import {
  fetchInsights,
  type InsightsPayload,
  type MilestonePayload,
  type PhasePayload,
} from "../api";

const TABS = [
  { id: "requirements", label: "Requirements" },
  { id: "waves", label: "Waves" },
  { id: "archives", label: "Archives" },
] as const;

type TabId = (typeof TABS)[number]["id"];

function statusBadgeClass(status: string | null, isGap: boolean): string {
  if (isGap) return "bg-red-900/40 text-red-400";
  if (status === "Complete") return "bg-green-900/40 text-[#4ec994]";
  if (status === "Pending") return "bg-yellow-900/40 text-yellow-400";
  return "bg-[#2a2d2e] text-[#858585]";
}

function statusBadgeLabel(status: string | null, isGap: boolean): string {
  if (isGap) return "Unmapped";
  return status ?? "Unknown";
}

function rowTintClass(isGap: boolean, status: string | null): string {
  if (isGap) return "bg-red-900/20";
  if (status === "Pending") return "bg-amber-900/20";
  return "";
}

function phaseBadgeClass(status: string): string {
  if (status === "complete" || status === "completed") return "bg-green-900/40 text-[#4ec994]";
  return "bg-[#2a2d2e] text-[#858585]";
}

function RequirementsTab({ data }: { data: InsightsPayload }) {
  const { requirements } = data;

  const grouped = useMemo(() => {
    const map = new Map<string, typeof requirements>();
    for (const req of requirements) {
      const arr = map.get(req.category) ?? [];
      arr.push(req);
      map.set(req.category, arr);
    }
    return map;
  }, [requirements]);

  if (requirements.length === 0) {
    return (
      <p className="text-[#858585] text-sm">No requirements found — REQUIREMENTS.md not present or empty.</p>
    );
  }

  return (
    <div>
      {[...grouped.entries()].map(([category, reqs]) => (
        <div key={category}>
          <p className="mt-4 mb-2 text-xs font-semibold uppercase tracking-wider text-[#858585]">
            {category}
          </p>
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="text-left text-xs text-[#858585]">
                <th className="border border-[#474747] px-3 py-2 font-medium">ID</th>
                <th className="border border-[#474747] px-3 py-2 font-medium">Description</th>
                <th className="border border-[#474747] px-3 py-2 font-medium">Phase</th>
                <th className="border border-[#474747] px-3 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {reqs.map((req) => (
                <tr key={req.id} className={rowTintClass(req.is_gap, req.status)}>
                  <td className="border border-[#474747] px-3 py-2 font-mono text-[#cccccc]">
                    {req.id}
                  </td>
                  <td className="border border-[#474747] px-3 py-2 text-[#cccccc]">
                    {req.description}
                  </td>
                  <td className="border border-[#474747] px-3 py-2 text-[#858585]">
                    {req.phase ?? "—"}
                  </td>
                  <td className="border border-[#474747] px-3 py-2">
                    <span
                      className={`rounded px-1.5 py-0.5 text-xs font-medium ${statusBadgeClass(req.status, req.is_gap)}`}
                    >
                      {statusBadgeLabel(req.status, req.is_gap)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}

function WavesTab({ data }: { data: InsightsPayload }) {
  const { wave_phases } = data;

  if (wave_phases.length === 0) {
    return (
      <p className="text-[#858585] text-sm">
        No multi-wave phases found — all phases have a single-wave execution plan.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {wave_phases.map((phase) => {
        const waveMap = new Map<number, string[]>();
        for (const plan of phase.plans) {
          const names = waveMap.get(plan.wave) ?? [];
          names.push(plan.plan_name);
          waveMap.set(plan.wave, names);
        }
        const sortedWaves = [...waveMap.entries()].sort(([a], [b]) => a - b);

        return (
          <div
            key={phase.phase_number}
            className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4"
          >
            <p className="mb-3 font-mono font-medium text-[#cccccc]">
              {String(phase.phase_number).padStart(2, "0")} — {phase.phase_title}
            </p>
            <div className="space-y-1">
              {sortedWaves.map(([wave, plans]) => (
                <div key={wave} className="flex items-start gap-3 text-sm">
                  <span className="shrink-0 rounded bg-[#2a2d2e] px-1.5 py-0.5 text-xs font-medium text-[#858585]">
                    Wave {wave}
                  </span>
                  <span className="text-[#cccccc]">{plans.join(", ")}</span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ArchiveItem({ milestone }: { milestone: MilestonePayload }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div>
      <button
        type="button"
        className="w-full rounded-md border border-[#474747] bg-[#1e1e1e] p-4 text-left transition-colors hover:bg-[#2a2d2e]"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#858585]">{expanded ? "\u2304" : "\u203A"}</span>
            <span className="font-medium text-[#cccccc]">{milestone.title}</span>
          </div>
          <span className="shrink-0 text-xs text-[#858585]">
            {milestone.completion_date ?? "date unknown"}
          </span>
        </div>
      </button>
      {expanded && (
        <div className="rounded-b-md border border-t-0 border-[#474747] bg-[#1e1e1e] p-4">
          {milestone.phases.length === 0 ? (
            <p className="text-sm text-[#858585]">No phases listed.</p>
          ) : (
            <div className="space-y-1">
              {(milestone.phases as PhasePayload[]).map((p) => (
                <div key={p.number} className="flex items-center gap-3 text-sm">
                  <span className="font-mono text-xs text-[#858585]">
                    {String(p.number).padStart(2, "0")}
                  </span>
                  <span className="flex-1 text-[#cccccc]">{p.title}</span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs font-medium ${phaseBadgeClass(p.status)}`}
                  >
                    {p.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ArchivesTab({ milestones }: { milestones: MilestonePayload[] }) {
  const archived = useMemo(
    () => milestones.filter((m) => m.is_archived === true),
    [milestones],
  );

  if (archived.length === 0) {
    return (
      <p className="text-[#858585] text-sm">
        No archived milestones — shipped milestones will appear here once marked as archived.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {archived.map((m) => (
        <ArchiveItem key={m.number} milestone={m} />
      ))}
    </div>
  );
}

export function InsightsPage() {
  const { activeProject, activeSegment, loading } = useApp();
  const [activeTab, setActiveTab] = useState<TabId>("requirements");
  const [insightsData, setInsightsData] = useState<InsightsPayload | null>(null);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [insightsError, setInsightsError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeSegment?.planningPath) return;
    setInsightsData(null);
    setInsightsError(null);
    setInsightsLoading(true);
    fetchInsights(activeSegment.planningPath)
      .then((data) => {
        setInsightsData(data);
      })
      .catch((e: unknown) => {
        setInsightsError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        setInsightsLoading(false);
      });
  }, [activeSegment?.planningPath]);

  if (loading) return <div className="p-6 text-[#858585] text-sm">Loading\u2026</div>;
  if (!activeProject)
    return (
      <div className="p-6 text-[#858585] text-sm">
        Add scan roots in Settings and select a project.
      </div>
    );

  return (
    <div className="p-6">
      <div className="mb-6 flex gap-1 border-b border-[#474747] pb-2">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              activeTab === tab.id
                ? "bg-[#2a2d2e] text-[#cccccc]"
                : "text-[#858585] hover:bg-[#2a2d2e] hover:text-[#cccccc]"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "requirements" && (
        <>
          {insightsLoading && (
            <p className="text-sm text-[#858585]">Loading requirements\u2026</p>
          )}
          {insightsError && (
            <p className="text-sm text-red-400">Error: {insightsError}</p>
          )}
          {insightsData && <RequirementsTab data={insightsData} />}
        </>
      )}

      {activeTab === "waves" && (
        <>
          {insightsLoading && (
            <p className="text-sm text-[#858585]">Loading wave data\u2026</p>
          )}
          {insightsError && (
            <p className="text-sm text-red-400">Error: {insightsError}</p>
          )}
          {insightsData && <WavesTab data={insightsData} />}
        </>
      )}

      {activeTab === "archives" && (
        <ArchivesTab milestones={activeProject.milestones} />
      )}
    </div>
  );
}
