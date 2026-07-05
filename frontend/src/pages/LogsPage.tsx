import { useCallback, useEffect, useRef, useState } from "react";
import { clearLogs, fetchLogs, type LogEntry } from "../api";

const LEVEL_COLORS: Record<string, string> = {
  DEBUG: "text-[#858585]",
  INFO: "text-[#9cdcfe]",
  WARNING: "text-[#dcdcaa]",
  ERROR: "text-[#f48771]",
  CRITICAL: "text-[#f44747]",
};

const LEVEL_BG: Record<string, string> = {
  WARNING: "bg-[#dcdcaa]/5",
  ERROR: "bg-[#f48771]/5",
  CRITICAL: "bg-[#f44747]/10",
};

const POLL_MS = 2000;

function fmtTs(ts: number): string {
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString(undefined, { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" }) +
    "." + String(d.getMilliseconds()).padStart(3, "0");
}

export function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<string>("ALL");
  const [autoScroll, setAutoScroll] = useState(true);
  const [clearing, setClearing] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    try {
      const entries = await fetchLogs();
      setLogs(entries);
    } catch {
      // silently ignore transient fetch errors
    }
  }, []);

  // Initial load + polling
  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), POLL_MS);
    return () => window.clearInterval(id);
  }, [load]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, autoScroll]);

  const handleScroll = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 60;
    setAutoScroll(atBottom);
  }, []);

  const handleClear = useCallback(async () => {
    setClearing(true);
    try {
      await clearLogs();
      setLogs([]);
    } finally {
      setClearing(false);
    }
  }, []);

  const levels = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];
  const visible = filter === "ALL" ? logs : logs.filter((e) => e.level === filter);

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#474747] px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-[#cccccc]">Diagnostic Logs</h2>
          <p className="text-xs text-[#858585]">Live backend log stream — refreshes every {POLL_MS / 1000}s</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Level filter */}
          <div className="flex gap-1">
            {levels.map((l) => (
              <button
                key={l}
                type="button"
                onClick={() => setFilter(l)}
                className={`rounded px-2 py-0.5 text-xs font-medium transition-colors ${
                  filter === l
                    ? "bg-[#2a2d2e] text-[#cccccc]"
                    : "text-[#858585] hover:text-[#cccccc]"
                }`}
              >
                {l}
              </button>
            ))}
          </div>
          <div className="h-4 w-px bg-[#474747]" />
          {/* Auto-scroll toggle */}
          <button
            type="button"
            onClick={() => setAutoScroll((v) => !v)}
            className={`rounded px-2 py-0.5 text-xs font-medium transition-colors ${
              autoScroll ? "bg-[#2a2d2e] text-[#9cdcfe]" : "text-[#858585] hover:text-[#cccccc]"
            }`}
            title="Toggle auto-scroll to latest"
          >
            ↓ auto
          </button>
          {/* Clear */}
          <button
            type="button"
            onClick={() => void handleClear()}
            disabled={clearing}
            className="rounded px-2 py-0.5 text-xs font-medium text-[#858585] hover:text-[#f48771] disabled:opacity-40"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Count badge */}
      <div className="border-b border-[#474747] px-4 py-1.5">
        <span className="text-xs text-[#858585]">
          {visible.length} entr{visible.length === 1 ? "y" : "ies"}
          {filter !== "ALL" && ` (${filter})`}
          {" · "}
          {logs.length} total
        </span>
      </div>

      {/* Log rows */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="min-h-0 flex-1 overflow-y-auto font-mono text-xs"
      >
        {visible.length === 0 ? (
          <p className="p-4 text-[#858585]">No log entries yet. The backend will populate this as it scans projects.</p>
        ) : (
          <table className="w-full border-collapse">
            <tbody>
              {visible.map((entry, i) => (
                <tr
                  key={i}
                  className={`border-b border-[#2a2d2e] ${LEVEL_BG[entry.level] ?? ""}`}
                >
                  <td className="whitespace-nowrap px-3 py-0.5 text-[#858585]">
                    {fmtTs(entry.ts)}
                  </td>
                  <td className={`w-16 whitespace-nowrap px-2 py-0.5 font-semibold ${LEVEL_COLORS[entry.level] ?? "text-[#cccccc]"}`}>
                    {entry.level}
                  </td>
                  <td className="max-w-[180px] truncate px-2 py-0.5 text-[#858585]" title={entry.logger}>
                    {entry.logger.replace("gsd_monitor.", "")}
                  </td>
                  <td className="break-all px-2 py-0.5 text-[#cccccc]">
                    {entry.message}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
