import { useMemo, useState } from "react";
import { useApp } from "../context";
import { fmtDate, statusLabel, statusBorderClass } from "../utils";

function driftBadgeClass(drift: string): string {
  switch (drift) {
    case "major":
      return "bg-red-900/40 text-red-400";
    case "minor":
      return "bg-yellow-900/40 text-yellow-400";
    case "none":
      return "bg-green-900/40 text-[#4ec994]";
    default:
      return "bg-[#2a2d2e] text-[#858585]";
  }
}

function driftLabel(drift: string): string {
  switch (drift) {
    case "major":
      return "Major";
    case "minor":
      return "Minor";
    case "none":
      return "None";
    default:
      return "Deferred";
  }
}

function planAgeDays(planWriteTime: string | null | undefined): number | null {
  if (!planWriteTime) return null;
  return Math.floor((Date.now() - new Date(planWriteTime).getTime()) / 86_400_000);
}

const DRIFT_ORDER: Record<string, number> = { major: 0, minor: 1, none: 2, deferred: 3 };

export function DriftPage() {
  const { activeProject, loading } = useApp();
  const [showDeferred, setShowDeferred] = useState(false);

  const allPhases = useMemo(
    () => activeProject?.milestones.flatMap((m) => m.phases) ?? [],
    [activeProject],
  );

  const activePhases = useMemo(
    () =>
      [...allPhases]
        .filter((p) => !(p.status === "not_started" && p.drift === "deferred"))
        .sort((a, b) => (DRIFT_ORDER[a.drift] ?? 99) - (DRIFT_ORDER[b.drift] ?? 99)),
    [allPhases],
  );

  const deferredPhases = useMemo(
    () => allPhases.filter((p) => p.status === "not_started" && p.drift === "deferred"),
    [allPhases],
  );

  if (loading) return <div className="p-6 text-[#858585] text-sm">Loading…</div>;
  if (!activeProject)
    return <div className="p-6 text-[#858585] text-sm">Add scan roots in Settings and select a project.</div>;

  return (
    <div className="p-6">
      {activePhases.length === 0 && deferredPhases.length === 0 ? (
        <p className="text-[#858585] text-sm">No drift data — all phases are on track or not yet started.</p>
      ) : (
        <>
          <div className="space-y-2">
            {activePhases.map((p) => (
              <div
                key={p.number}
                className={`w-full rounded-md border border-[#474747] border-l-[3px] ${statusBorderClass(p.status)} bg-[#1e1e1e] p-4`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono font-medium text-[#cccccc]">
                    {String(p.number).padStart(2, "0")} — {p.title}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-[#858585]">{statusLabel(p.status)}</span>
                    <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${driftBadgeClass(p.drift)}`}>
                      {driftLabel(p.drift)}
                    </span>
                    <span className="text-xs text-[#858585]">
                      {(() => {
                        const age = planAgeDays(p.plan_write_time);
                        return age !== null ? `${age} day${age === 1 ? "" : "s"}` : "—";
                      })()}
                    </span>
                    <span className="text-xs text-[#858585]">{fmtDate(p.last_updated)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {deferredPhases.length > 0 && (
            <>
              <button
                type="button"
                className="mt-4 flex items-center gap-1 text-xs text-[#858585] hover:text-[#cccccc]"
                onClick={() => setShowDeferred((v) => !v)}
                aria-expanded={showDeferred}
                aria-controls="deferred-phases"
              >
                <span>{showDeferred ? "⌄" : "›"}</span>
                <span>
                  {showDeferred ? "Hide un-started phases" : `Show ${deferredPhases.length} un-started phases`}
                </span>
              </button>
              {showDeferred && (
                <div id="deferred-phases" className="mt-2 space-y-2 opacity-60">
                  {deferredPhases.map((p) => (
                    <div
                      key={p.number}
                      className={`w-full rounded-md border border-[#474747] border-l-[3px] ${statusBorderClass(p.status)} bg-[#1e1e1e] p-4`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-mono font-medium text-[#cccccc]">
                          {String(p.number).padStart(2, "0")} — {p.title}
                        </span>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-[#858585]">{statusLabel(p.status)}</span>
                          <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${driftBadgeClass(p.drift)}`}>
                            {driftLabel(p.drift)}
                          </span>
                          <span className="text-xs text-[#858585]">
                            {(() => {
                              const age = planAgeDays(p.plan_write_time);
                              return age !== null ? `${age} day${age === 1 ? "" : "s"}` : "—";
                            })()}
                          </span>
                          <span className="text-xs text-[#858585]">{fmtDate(p.last_updated)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
