import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { useApp } from "../context";
import {
  fetchArtifacts,
  fetchDocFile,
  openDocFile,
  type ArtifactEntry,
  type ArtifactsPayload,
} from "../api";

type ArtifactTab = "spikes" | "threads" | "codebase" | "intel" | "sketches";

const TAB_LABELS: Record<ArtifactTab, string> = {
  spikes: "Spikes",
  threads: "Threads",
  codebase: "Codebase",
  intel: "Intel",
  sketches: "Sketches",
};

export function ArtifactsPage() {
  const { activeSegment, loading } = useApp();
  const [artifacts, setArtifacts] = useState<ArtifactsPayload | null>(null);
  const [loadingArtifacts, setLoadingArtifacts] = useState(false);
  const [activeTab, setActiveTab] = useState<ArtifactTab>("spikes");
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [loadingFile, setLoadingFile] = useState(false);

  const planningPath = activeSegment?.planningPath ?? null;

  useEffect(() => {
    setArtifacts(null);
    setSelectedPath(null);
    setFileContent(null);
    if (!planningPath) return;
    setLoadingArtifacts(true);
    void fetchArtifacts(planningPath)
      .then((data) => {
        setArtifacts(data);
        // Auto-select first non-empty tab
        const tabs: ArtifactTab[] = ["spikes", "threads", "codebase", "intel", "sketches"];
        for (const tab of tabs) {
          if (data[tab].length > 0) {
            setActiveTab(tab);
            break;
          }
        }
      })
      .finally(() => setLoadingArtifacts(false));
  }, [planningPath]);

  function openFile(entry: ArtifactEntry) {
    if (!planningPath) return;
    const filePath = entry.preview_file ?? entry.path;
    if (activeTab === "sketches") {
      // Sketches open externally
      void openDocFile(planningPath, filePath);
      return;
    }
    setSelectedPath(filePath);
    setFileContent(null);
    setLoadingFile(true);
    void fetchDocFile(planningPath, filePath)
      .then((data) => setFileContent(data.content))
      .finally(() => setLoadingFile(false));
  }

  if (loading) return <div className="p-6 text-[#858585] text-sm">Loading\u2026</div>;
  if (!activeSegment)
    return (
      <div className="p-6 text-[#858585] text-sm">
        Add scan roots in Settings and select a project.
      </div>
    );

  const entries: ArtifactEntry[] = artifacts?.[activeTab] ?? [];
  // Only show tabs that have content
  const availableTabs = (["spikes", "threads", "codebase", "intel", "sketches"] as ArtifactTab[]).filter(
    (t) => (artifacts?.[t]?.length ?? 0) > 0,
  );

  return (
    <div className="flex h-full">
      {/* Left panel — artifact list */}
      <div className="w-64 shrink-0 border-r border-[#474747] flex flex-col">
        {/* Tab bar */}
        <div className="flex flex-wrap gap-1 border-b border-[#474747] p-2">
          {loadingArtifacts ? (
            <span className="text-xs text-[#858585]">Loading\u2026</span>
          ) : availableTabs.length === 0 ? (
            <span className="text-xs text-[#858585]">No artifacts</span>
          ) : (
            availableTabs.map((tab) => (
              <button
                key={tab}
                type="button"
                className={`rounded px-2 py-0.5 text-xs font-medium transition-colors ${
                  activeTab === tab
                    ? "bg-[#007acc]/30 text-[#cccccc]"
                    : "text-[#858585] hover:text-[#cccccc]"
                }`}
                onClick={() => {
                  setActiveTab(tab);
                  setSelectedPath(null);
                  setFileContent(null);
                }}
              >
                {TAB_LABELS[tab]}
              </button>
            ))
          )}
        </div>

        {/* File list */}
        <div className="flex-1 overflow-y-auto">
          {entries.length === 0 ? (
            <div className="p-4 text-xs text-[#858585]">
              No {TAB_LABELS[activeTab].toLowerCase()} found.
            </div>
          ) : (
            <ul>
              {entries.map((entry) => (
                <li key={entry.path}>
                  <button
                    type="button"
                    className={`w-full px-3 py-2 text-left text-xs transition-colors hover:bg-[#2a2d2e] ${
                      selectedPath === (entry.preview_file ?? entry.path)
                        ? "bg-[#37373d] text-[#cccccc]"
                        : "text-[#858585]"
                    }`}
                    onClick={() => openFile(entry)}
                  >
                    <span className="block truncate font-mono">{entry.name}</span>
                    {activeTab === "sketches" && (
                      <span className="text-[10px] text-[#474747]">opens externally</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Right panel — file detail */}
      <div className="flex-1 overflow-y-auto p-4">
        {loadingFile && (
          <div className="text-xs text-[#858585]">Loading\u2026</div>
        )}
        {!loadingFile && fileContent !== null && (
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
              {fileContent}
            </ReactMarkdown>
          </div>
        )}
        {!loadingFile && fileContent === null && !loadingArtifacts && (
          <div className="text-xs text-[#858585]">
            {availableTabs.length === 0
              ? "No artifact directories found in this project."
              : "Select an artifact to view its content."}
          </div>
        )}
      </div>
    </div>
  );
}
