import { useEffect, useMemo, useState } from "react";
import { useApp } from "../context";
import { fetchQuickTasks } from "../api";
import type { QuickTaskPayload } from "../api";
import { fmtDate } from "../utils";

function taskStatusBadgeClass(status: string): string {
  switch (status) {
    case "in_progress":
      return "bg-yellow-900/40 text-yellow-400";
    case "complete":
      return "bg-green-900/40 text-[#4ec994]";
    default:
      return "bg-[#2a2d2e] text-[#858585]";
  }
}

function taskStatusLabel(status: string): string {
  switch (status) {
    case "in_progress":
      return "In progress";
    case "complete":
      return "Complete";
    default:
      return "Open";
  }
}

export function QuickTasksPage() {
  const { activeSegment, loading } = useApp();
  const [tasks, setTasks] = useState<QuickTaskPayload[]>([]);
  const [fetchLoading, setFetchLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeSegment?.planningPath) return;
    setFetchLoading(true);
    void fetchQuickTasks(activeSegment.planningPath)
      .then((t) => {
        setTasks(t);
        setError(null);
      })
      .catch(() =>
        setError(
          "Could not load quick tasks. Check your project path and try refreshing.",
        ),
      )
      .finally(() => setFetchLoading(false));
  }, [activeSegment?.planningPath]);

  const sorted = useMemo(
    () =>
      [...tasks].sort((a, b) => {
        if (a.last_updated && b.last_updated)
          return b.last_updated.localeCompare(a.last_updated);
        if (a.last_updated) return -1;
        if (b.last_updated) return 1;
        return 0;
      }),
    [tasks],
  );

  if (loading || fetchLoading)
    return (
      <div className="p-6 text-[#858585] text-sm">Loading\u2026</div>
    );
  if (!activeSegment)
    return (
      <div className="p-6 text-[#858585] text-sm">
        Add scan roots in Settings and select a project.
      </div>
    );
  if (error)
    return (
      <div className="p-6">
        <p className="text-red-400 text-sm">{error}</p>
      </div>
    );
  if (sorted.length === 0)
    return (
      <div className="p-6 text-center text-[#858585] text-sm">
        <p className="font-medium">No quick tasks yet</p>
        <p>Quick tasks appear here when you run /gsd:quick in this project.</p>
      </div>
    );

  return (
    <div className="p-6 space-y-2">
      {sorted.map((t) => (
        <div
          key={t.file_path}
          className="rounded-md border border-[#474747] bg-[#1e1e1e] p-4"
        >
          <div className="flex items-center justify-between gap-2">
            <span className="text-sm font-medium text-[#cccccc]">
              {t.title}
            </span>
            <div className="flex items-center gap-3">
              <span
                className={`rounded px-1.5 py-0.5 text-xs font-medium ${taskStatusBadgeClass(t.status)}`}
              >
                {taskStatusLabel(t.status)}
              </span>
              <span className="text-xs text-[#858585]">
                {fmtDate(t.created)}
              </span>
              <span className="text-xs text-[#858585]">
                {fmtDate(t.last_updated)}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
