import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { useApp } from "../context";
import { statusBorderClass } from "../utils";

function validationBadgeClass(hasValidation: boolean): string {
  return hasValidation
    ? "bg-green-900/40 text-[#4ec994]"
    : "bg-[#2a2d2e] text-[#858585]";
}

function nyquistBadgeClass(nyquistCompliant: boolean | null | undefined): string {
  if (nyquistCompliant === true) return "bg-green-900/40 text-[#4ec994]";
  if (nyquistCompliant === false) return "bg-red-900/40 text-red-400";
  return "bg-[#2a2d2e] text-[#858585]";
}

function nyquistLabel(nyquistCompliant: boolean | null | undefined): string {
  if (nyquistCompliant === true) return "Pass";
  if (nyquistCompliant === false) return "Fail";
  return "Unknown";
}

function uatBadgeClass(hasUat: boolean): string {
  return hasUat
    ? "bg-green-900/40 text-[#4ec994]"
    : "bg-[#2a2d2e] text-[#858585]";
}

export function VerificationPage() {
  const { activeProject, activeSegment, loading } = useApp();
  const [expandedPhase, setExpandedPhase] = useState<number | null>(null);
  const [showNoValidation, setShowNoValidation] = useState(false);

  useEffect(() => {
    setExpandedPhase(null);
  }, [activeSegment?.planningPath]);

  const allPhases = useMemo(
    () =>
      [...(activeProject?.milestones.flatMap((m) => m.phases) ?? [])].sort(
        (a, b) => a.number - b.number,
      ),
    [activeProject],
  );

  const validatedPhases = useMemo(
    () => allPhases.filter((p) => p.has_validation),
    [allPhases],
  );

  const unvalidatedPhases = useMemo(
    () => allPhases.filter((p) => !p.has_validation),
    [allPhases],
  );

  if (loading) return <div className="p-6 text-[#858585] text-sm">Loading\u2026</div>;
  if (!activeProject)
    return (
      <div className="p-6 text-[#858585] text-sm">
        Add scan roots in Settings and select a project.
      </div>
    );
  if (allPhases.length === 0)
    return (
      <div className="p-6 text-[#858585] text-sm">No phases found for this project.</div>
    );

  return (
    <div className="p-6">
      <div className="space-y-2">
        {validatedPhases.map((p) => (
          <div key={p.number}>
            <button
              type="button"
              className={`w-full rounded-md border border-[#474747] border-l-[3px] ${statusBorderClass(p.status)} bg-[#1e1e1e] p-4 text-left transition-colors hover:bg-[#2a2d2e]`}
              onClick={() =>
                setExpandedPhase((n) => (n === p.number ? null : p.number))
              }
              aria-expanded={expandedPhase === p.number}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#858585]">
                    {expandedPhase === p.number ? "\u2304" : "\u203A"}
                  </span>
                  <span className="font-mono font-medium text-[#cccccc]">
                    {String(p.number).padStart(2, "0")} &mdash; {p.title}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs font-medium ${validationBadgeClass(p.has_validation)}`}
                  >
                    {p.has_validation ? "Validated" : "None"}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs font-medium ${nyquistBadgeClass(p.nyquist_compliant)}`}
                  >
                    {nyquistLabel(p.nyquist_compliant)}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs font-medium ${uatBadgeClass(p.has_uat)}`}
                  >
                    {p.has_uat ? "UAT" : "No UAT"}
                  </span>
                </div>
              </div>
            </button>
            {expandedPhase === p.number && p.validation_content && (
              <div className="rounded-b-md border border-t-0 border-[#474747] bg-[#1e1e1e] p-4">
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                    {p.validation_content}
                  </ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {unvalidatedPhases.length > 0 && (
        <>
          <button
            type="button"
            className="mt-4 flex items-center gap-1 text-xs text-[#858585] hover:text-[#cccccc]"
            onClick={() => setShowNoValidation((v) => !v)}
            aria-expanded={showNoValidation}
            aria-controls="unvalidated-phases"
          >
            <span>{showNoValidation ? "\u2304" : "\u203A"}</span>
            <span>
              {showNoValidation
                ? "Hide phases without validation"
                : `Show ${unvalidatedPhases.length} phases without validation`}
            </span>
          </button>
          {showNoValidation && (
            <div id="unvalidated-phases" className="mt-2 space-y-2 opacity-60">
              {unvalidatedPhases.map((p) => (
                <div
                  key={p.number}
                  className={`w-full rounded-md border border-[#474747] border-l-[3px] ${statusBorderClass(p.status)} bg-[#1e1e1e] p-4`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[#858585]">{" "}</span>
                      <span className="font-mono font-medium text-[#cccccc]">
                        {String(p.number).padStart(2, "0")} &mdash; {p.title}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-1.5 py-0.5 text-xs font-medium ${validationBadgeClass(false)}`}
                      >
                        None
                      </span>
                      <span
                        className={`rounded px-1.5 py-0.5 text-xs font-medium ${nyquistBadgeClass(p.nyquist_compliant)}`}
                      >
                        {nyquistLabel(p.nyquist_compliant)}
                      </span>
                      <span
                        className={`rounded px-1.5 py-0.5 text-xs font-medium ${uatBadgeClass(p.has_uat)}`}
                      >
                        {p.has_uat ? "UAT" : "No UAT"}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
