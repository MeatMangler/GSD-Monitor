import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { useApp } from "../context";
import { fetchDocTree, fetchDocFile, openDocFile } from "../api";
import type { DocTreeNode } from "../api";

export function DocsPage() {
  const [tree, setTree] = useState<DocTreeNode[]>([]);
  const [selectedPath, setSelectedPath] = useState<string>("ROADMAP.md");
  const [content, setContent] = useState<string>("");
  const [contentLoading, setContentLoading] = useState<boolean>(false);
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());
  const [treeError, setTreeError] = useState<string | null>(null);
  const [contentError, setContentError] = useState<string | null>(null);
  const [fileMeta, setFileMeta] = useState<{ createdAt: string | null; modifiedAt: string | null } | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [sidebarWidth, setSidebarWidth] = useState(260);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [resizing, setResizing] = useState(false);
  const [autoOpen, setAutoOpen] = useState(false);
  const [dragHover, setDragHover] = useState(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(0);

  const { activeSegment, activeProject, loading, groups } = useApp();

  // Active PLAN.md resolution (D-07)
  const activePlanPath = useMemo(() => {
    if (!activeProject || !activeSegment) return null;
    const phases = activeProject.milestones.flatMap((m) => m.phases);
    const inProgress = phases.find((p) => p.status === "in_progress");
    if (!inProgress) return null;
    const planArtifact = inProgress.artifact_paths
      .filter((a) => a.endsWith("-PLAN.md"))
      .sort()
      .at(-1);
    if (!planArtifact) return null;
    const root = activeSegment.planningPath;
    return planArtifact.startsWith(root)
      ? planArtifact.slice(root.length).replace(/^[/\\]+/, "").replace(/\\/g, "/")
      : null;
  }, [activeProject, activeSegment]);

  // Active plan label via useMemo
  const activePlanLabel = useMemo(() => {
    if (!activeProject) return null;
    const phases = activeProject.milestones.flatMap((m) => m.phases);
    const inProgress = phases.find((p) => p.status === "in_progress");
    if (!inProgress) return null;
    return `PLAN (${String(inProgress.number).padStart(2, "0")})`;
  }, [activeProject]);

  // Helper: convert an absolute artifact path to a planning-root-relative path
  function toRelPath(root: string, absPath: string): string | null {
    return absPath.startsWith(root)
      ? absPath.slice(root.length).replace(/^[/\\]+/, "").replace(/\\/g, "/")
      : null;
  }

  // Quick-access items — per UI-SPEC section 4, DOCS-01 through DOCS-05
  const quickAccess = useMemo(() => {
    const items: { label: string; path: string }[] = [
      { label: "ROADMAP.md", path: "ROADMAP.md" },
      { label: "STATE.md", path: "STATE.md" },
    ];
    if (activePlanPath && activePlanLabel) {
      items.push({ label: activePlanLabel, path: activePlanPath });
    }
    items.push({ label: "REQUIREMENTS.md", path: "REQUIREMENTS.md" });

    // Add quick-access for new doc types when present on the in-progress phase
    if (activeProject && activeSegment) {
      const phases = activeProject.milestones.flatMap((m) => m.phases);
      const inProgress = phases.find((p) => p.status === "in_progress");
      if (inProgress) {
        const root = activeSegment.planningPath;
        const padded = String(inProgress.number).padStart(2, "0");

        // VERIFICATION — per DOCS-01, has_validation flag
        if (inProgress.has_validation) {
          const artifact = inProgress.artifact_paths.find((a) => a.endsWith("-VERIFICATION.md"));
          if (artifact) {
            const rel = toRelPath(root, artifact);
            if (rel) items.push({ label: `VERIFICATION (${padded})`, path: rel });
          }
        }

        // UI-SPEC — per DOCS-02, has_ui_spec flag
        if (inProgress.has_ui_spec) {
          const artifact = inProgress.artifact_paths.find((a) => a.endsWith("-UI-SPEC.md"));
          if (artifact) {
            const rel = toRelPath(root, artifact);
            if (rel) items.push({ label: `UI-SPEC (${padded})`, path: rel });
          }
        }

        // UI-REVIEW — per DOCS-03, has_ui_review flag
        if (inProgress.has_ui_review) {
          const artifact = inProgress.artifact_paths.find((a) => a.endsWith("-UI-REVIEW.md"));
          if (artifact) {
            const rel = toRelPath(root, artifact);
            if (rel) items.push({ label: `UI-REVIEW (${padded})`, path: rel });
          }
        }

        // SUMMARY — per DOCS-04, has_summary flag
        if (inProgress.has_summary) {
          const artifact = inProgress.artifact_paths.find((a) => a.endsWith("-SUMMARY.md"));
          if (artifact) {
            const rel = toRelPath(root, artifact);
            if (rel) items.push({ label: `SUMMARY (${padded})`, path: rel });
          }
        }
      }
    }

    return items;
  }, [activePlanPath, activePlanLabel, activeProject, activeSegment]);

  // Increment refreshKey whenever groups changes, but skip the initial render
  const isInitialMount = useRef(true);
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    setRefreshKey((k) => k + 1);
  }, [groups]);

  // Reset on project change (D-19)
  useEffect(() => {
    setSelectedPath("ROADMAP.md");
    setExpandedDirs(new Set());
    setContent("");
    setContentError(null);
    setTreeError(null);
    setFileMeta(null);
  }, [activeSegment?.planningPath]);

  // Fetch tree when segment changes or groups refresh
  useEffect(() => {
    if (!activeSegment?.planningPath) return;
    void fetchDocTree(activeSegment.planningPath)
      .then((t) => {
        setTree(t);
        setTreeError(null);
      })
      .catch(() => {
        setTree([]);
        setTreeError(
          "Could not load file tree. Try switching projects or restarting the app.",
        );
      });
  }, [activeSegment?.planningPath, refreshKey]);

  // Fetch file content when selectedPath changes or groups refresh
  useEffect(() => {
    if (!activeSegment?.planningPath || !selectedPath) return;
    setContentLoading(true);
    setContentError(null);
    void fetchDocFile(activeSegment.planningPath, selectedPath)
      .then((r) => {
        setContent(r.content);
        setContentError(null);
        setFileMeta({ createdAt: r.created_at, modifiedAt: r.modified_at });
      })
      .catch(() => {
        setContent("");
        setContentError(
          "Could not load file. Check that the file still exists and try selecting it again.",
        );
        setFileMeta(null);
      })
      .finally(() => setContentLoading(false));
  }, [activeSegment?.planningPath, selectedPath, refreshKey]);

  function formatDateTime(iso: string | null): string {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      year: "numeric", month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
  }

  function handleOpenExternal() {
    if (!activeSegment?.planningPath || !selectedPath) return;
    void openDocFile(activeSegment.planningPath, selectedPath).catch(() => {});
  }

  function handleFileClick(path: string) {
    if (path !== selectedPath) setSelectedPath(path);
    if (autoOpen && activeSegment?.planningPath) {
      void openDocFile(activeSegment.planningPath, path).catch(() => {});
    }
  }

  function handleDirToggle(path: string) {
    setExpandedDirs((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  }

  function renderTreeNode(node: DocTreeNode, depth: number): ReactNode {
    if (node.type === "dir") {
      const isExpanded = expandedDirs.has(node.path);
      return (
        <div key={node.path}>
          <button
            type="button"
            className={`flex items-center w-full text-left min-h-7 px-2 hover:bg-[#2a2d2e] ${isExpanded ? "text-[#cccccc]" : "text-[#858585]"} hover:text-[#cccccc]`}
            style={{ paddingLeft: `${8 + depth * 16}px` }}
            onClick={() => handleDirToggle(node.path)}
            aria-expanded={isExpanded}
          >
            <span className="inline-block w-3 text-center text-xs text-[#858585] mr-1 select-none">
              {isExpanded ? "⌄" : "›"}
            </span>
            <span className="font-mono text-xs truncate">{node.name}</span>
          </button>
          {isExpanded &&
            node.children.map((child) => renderTreeNode(child, depth + 1))}
        </div>
      );
    }
    const isSelected = node.path === selectedPath;
    return (
      <button
        key={node.path}
        type="button"
        className={`flex items-center w-full text-left min-h-7 px-2 hover:bg-[#2a2d2e] hover:text-[#cccccc] ${isSelected ? "bg-[#2a2d2e] text-[#007acc]" : "text-[#858585]"}`}
        style={{ paddingLeft: `${8 + depth * 16}px` }}
        onClick={() => handleFileClick(node.path)}
        aria-current={isSelected ? "true" : undefined}
      >
        <span className="inline-block w-3 mr-1 select-none" />
        <span className="font-mono text-xs truncate">{node.name}</span>
      </button>
    );
  }

  // Shared auto-open checkbox rendered in both section headers
  function AutoOpenCheckbox() {
    return (
      <label className="flex items-center gap-1 cursor-pointer select-none ml-auto shrink-0">
        <input
          type="checkbox"
          checked={autoOpen}
          onChange={(e) => setAutoOpen(e.target.checked)}
          className="w-3 h-3 accent-[#4ec994]"
        />
        <span className="text-[10px] text-[#858585] whitespace-nowrap">auto-open</span>
      </label>
    );
  }

  const canOpenExternal = !contentLoading && !contentError && !!selectedPath && !!activeSegment;

  return (
    <div className="flex h-full" style={{ userSelect: resizing ? "none" : undefined }}>
      {!activeSegment ? (
        <div className="p-6 text-[#858585] text-sm">
          Add scan roots in Settings and select a project.
        </div>
      ) : loading ? (
        <div className="p-6 text-[#858585] text-sm">Loading...</div>
      ) : (
        <>
          {/* Sidebar */}
          <aside
            className="shrink-0 bg-[#252526] flex flex-col"
            style={{
              width: sidebarCollapsed ? "28px" : `${sidebarWidth}px`,
              overflow: sidebarCollapsed ? "hidden" : "auto",
            }}
            role="navigation"
            aria-label="Planning files"
          >
            {/* Collapse / expand toggle — always visible */}
            <button
              type="button"
              title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              className="shrink-0 w-full flex items-center justify-between px-2 py-1.5 border-b border-[#474747] text-[#858585] hover:text-[#cccccc] hover:bg-[#2a2d2e] select-none"
              onClick={() => setSidebarCollapsed((c) => !c)}
            >
              {!sidebarCollapsed && <span className="text-[10px] font-medium uppercase tracking-wider">Explorer</span>}
              <span className="text-base leading-none">{sidebarCollapsed ? "›" : "‹"}</span>
            </button>

            {!sidebarCollapsed && (
              <>
                <div className="px-2 py-1 text-xs font-medium uppercase tracking-wider text-[#858585] flex items-center gap-1">
                  <span>Quick access</span>
                  <AutoOpenCheckbox />
                </div>
                {quickAccess.map((item) => (
                  <button
                    key={item.path}
                    type="button"
                    className={`flex items-center w-full text-left min-h-7 px-2 hover:bg-[#2a2d2e] hover:text-[#cccccc] ${
                      selectedPath === item.path
                        ? "bg-[#2a2d2e] text-[#007acc]"
                        : "text-[#858585]"
                    }`}
                    onClick={() => handleFileClick(item.path)}
                    aria-current={selectedPath === item.path ? "true" : undefined}
                  >
                    <span className="inline-block w-3 mr-1 select-none" />
                    <span className="font-mono text-xs truncate">{item.label}</span>
                  </button>
                ))}
                <hr className="border-[#474747] my-2" />
                <div className="px-2 py-1 text-xs font-medium uppercase tracking-wider text-[#858585] flex items-center gap-1">
                  <span>Files</span>
                  <AutoOpenCheckbox />
                </div>
                {treeError ? (
                  <p className="text-red-400 text-sm px-2 py-1">{treeError}</p>
                ) : (
                  tree.map((node) => renderTreeNode(node, 0))
                )}
              </>
            )}
          </aside>

          {/* Drag-to-resize handle — only when sidebar is expanded */}
          {!sidebarCollapsed && (
            <div
              className="w-2 shrink-0 cursor-col-resize select-none"
              style={{ background: resizing || dragHover ? "#007acc" : "#474747" }}
              role="separator"
              aria-orientation="vertical"
              title="Drag to resize"
              onPointerEnter={() => setDragHover(true)}
              onPointerLeave={() => setDragHover(false)}
              onPointerDown={(e) => {
                e.currentTarget.setPointerCapture(e.pointerId);
                dragStartX.current = e.clientX;
                dragStartWidth.current = sidebarWidth;
                setResizing(true);
              }}
              onPointerMove={(e) => {
                if (!e.currentTarget.hasPointerCapture(e.pointerId)) return;
                const delta = e.clientX - dragStartX.current;
                setSidebarWidth(Math.min(480, Math.max(160, dragStartWidth.current + delta)));
              }}
              onPointerUp={(e) => {
                e.currentTarget.releasePointerCapture(e.pointerId);
                setDragHover(false);
                setResizing(false);
              }}
            />
          )}

          {/* Main content area */}
          <main
            className="flex-1 flex flex-col min-h-0 bg-[#1e1e1e]"
            role="region"
            aria-label="Document content"
          >
            {/* Compact toolbar */}
            <div className="shrink-0 border-b border-[#474747] bg-[#252526] px-4 py-1 flex items-center justify-end min-h-[30px]">
              {canOpenExternal && (
                <button
                  type="button"
                  onClick={handleOpenExternal}
                  title="Open in default external application"
                  className="flex items-center gap-1 text-xs text-[#858585] hover:text-[#cccccc] px-2 py-0.5 rounded border border-[#474747] hover:border-[#858585] hover:bg-[#1e1e1e]"
                >
                  <span>↗</span>
                  <span>Open</span>
                </button>
              )}
            </div>

            <div className="flex-1 overflow-auto p-6">
              {contentLoading ? (
                <p className="text-[#858585] text-sm">Loading...</p>
              ) : contentError ? (
                <p className="text-red-400 text-sm">{contentError}</p>
              ) : selectedPath.endsWith(".md") ? (
                <div className="docs-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                    {content}
                  </ReactMarkdown>
                </div>
              ) : (
                <pre className="text-sm text-[#cccccc] whitespace-pre-wrap font-mono">
                  {content}
                </pre>
              )}
            </div>

            {fileMeta && !contentLoading && (
              <footer className="shrink-0 border-t border-[#474747] bg-[#252526] px-6 py-2 flex items-center gap-6 text-xs text-[#858585] font-mono">
                <span className="text-[#6a9955] truncate max-w-[280px]" title={selectedPath}>
                  {selectedPath.split("/").pop()}
                </span>
                <span>
                  <span className="text-[#569cd6]">Modified:</span>{" "}
                  {formatDateTime(fileMeta.modifiedAt)}
                </span>
                <span>
                  <span className="text-[#569cd6]">Created:</span>{" "}
                  {formatDateTime(fileMeta.createdAt)}
                </span>
                <button
                  type="button"
                  onClick={handleOpenExternal}
                  className="ml-auto text-[#569cd6] hover:underline cursor-pointer"
                >
                  open externally ↗
                </button>
              </footer>
            )}
          </main>
        </>
      )}
    </div>
  );
}
