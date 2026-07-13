const base = "";

/** Avoid stale settings/groups when the embedded WebView caches GET responses. */
const noStore: RequestInit = { cache: "no-store" };

export async function fetchGroups(): Promise<GroupPayload[]> {
  const r = await fetch(`${base}/api/groups`, noStore);
  if (!r.ok) throw new Error(await r.text());
  const j = await r.json();
  return j.groups ?? [];
}

export async function refreshGroups(): Promise<GroupPayload[]> {
  const r = await fetch(`${base}/api/groups/refresh`, { ...noStore, method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  const j = await r.json();
  return j.groups ?? [];
}

/** Normalizes API or legacy PascalCase keys from GET /api/settings. */
export function scanRootsFromSettings(s: Record<string, unknown>): string[] {
  const r = s.scan_roots ?? s.ScanRoots;
  if (!Array.isArray(r)) return [];
  return r.map((x) => String(x).trim()).filter(Boolean);
}

export async function fetchSettings(): Promise<Record<string, unknown>> {
  const r = await fetch(`${base}/api/settings`, noStore);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function saveSettings(body: Record<string, unknown>): Promise<void> {
  const r = await fetch(`${base}/api/settings`, {
    ...noStore,
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
}

export async function browseFolders(): Promise<{ paths: string[]; cancelled: boolean }> {
  const r = await fetch(`${base}/api/browse-folder`, { ...noStore, method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ paths: string[]; cancelled: boolean }>;
}

export async function fetchQuickTasks(planningPath: string): Promise<QuickTaskPayload[]> {
  const enc = encodeURIComponent(planningPath);
  const r = await fetch(`${base}/api/quick-tasks/${enc}`, noStore);
  if (!r.ok) throw new Error(await r.text());
  const j = await r.json();
  return j.tasks ?? [];
}

export interface QuickTaskPayload {
  title: string;
  status: string;
  file_path: string;
  created?: string;
  last_updated?: string;
}

export interface RequirementEntryPayload {
  id: string;
  category: string;
  description: string;
  is_checked: boolean;
  phase: string | null;
  status: string | null;
  is_gap: boolean;
}

export interface PlanWaveEntry {
  plan_name: string;
  wave: number;
}

export interface PhaseWavePayload {
  phase_number: number;
  phase_title: string;
  plans: PlanWaveEntry[];
}

export interface InsightsPayload {
  requirements: RequirementEntryPayload[];
  wave_phases: PhaseWavePayload[];
}

export async function fetchInsights(planningPath: string): Promise<InsightsPayload> {
  const enc = encodeURIComponent(planningPath);
  const r = await fetch(`${base}/api/insights/${enc}`, noStore);
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<InsightsPayload>;
}

export interface WorktreeInfo {
  path: string;
  branch: string;
  isPrimary: boolean;
}

export interface GroupPayload {
  id: string;
  rootPath: string;
  displayName: string;
  isWorkspace: boolean;
  defaultSegmentKey: string | null;
  activeWorkstreamHint: string | null;
  segments: SegmentPayload[];
  worktrees: WorktreeInfo[];
}

export interface SegmentPayload {
  segmentKey: string;
  gsdProject: string | null;
  workstream: string | null;
  gsdVersion: string;
  planningPath: string;
  repoRoot: string;
  quickPlanningRoot: string;
  groupId: string;
  project: GsdProjectPayload;
  stateCurrentPosition?: string | null;
}

export interface GsdProjectPayload {
  name: string;
  path: string;
  description?: string | null;
  last_updated?: string | null;
  milestones: MilestonePayload[];
  version: string;
  handoff_info?: { phase?: string; plan?: string; timestamp?: string; paused?: boolean } | null;
  continue_here?: boolean;
  config_info?: { workflow_mode?: string; model_profile?: string; branching_strategy?: string } | null;
  progress_percent?: number;
  completed_phases?: number;
  total_phases?: number;
}

export interface MilestonePayload {
  title: string;
  number: number;
  status: string;
  progress: number;
  phases: PhasePayload[];
  code?: string | null;
  vision?: string | null;
  is_archived?: boolean;
  completion_date?: string | null;
}

export interface PhasePayload {
  number: number;
  title: string;
  status: string;
  drift: string;
  goal?: string | null;
  plan_content?: string | null;
  todos: { is_checked: boolean; text: string }[];
  artifact_paths: string[];
  last_updated?: string | null;
  plan_write_time?: string | null;
  has_context: boolean;
  has_research: boolean;
  has_plan: boolean;
  has_validation: boolean;
  has_ui_spec: boolean;
  has_ui_review: boolean;
  has_summary: boolean;
  has_requirements: boolean;
  nyquist_compliant?: boolean | null;
  research_coverage: string;
  research_content?: string | null;
  validation_content?: string | null;
  is_archived: boolean;
  archive_milestone?: string | null;
  code?: string | null;
  risk_tag?: string | null;
  depends_on: string[];
  has_uat: boolean;
}

export interface DocTreeNode {
  name: string;
  path: string;   // relative to planning root, forward slashes
  type: "file" | "dir";
  children: DocTreeNode[];
}

export interface DocFileResponse {
  content: string;
  created_at: string | null;
  modified_at: string | null;
}

export async function fetchDocTree(planningPath: string): Promise<DocTreeNode[]> {
  const enc = encodeURIComponent(planningPath);
  const r = await fetch(`${base}/api/docs/${enc}/tree`, noStore);
  if (!r.ok) throw new Error(await r.text());
  const j = await r.json();
  return j.tree ?? [];
}

export async function fetchDocFile(planningPath: string, relPath: string): Promise<DocFileResponse> {
  const enc = encodeURIComponent(planningPath);
  const params = new URLSearchParams({ path: relPath });
  const r = await fetch(`${base}/api/docs/${enc}/file?${params}`, noStore);
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<DocFileResponse>;
}

export async function openDocFile(planningPath: string, relPath: string): Promise<void> {
  const enc = encodeURIComponent(planningPath);
  const params = new URLSearchParams({ path: relPath });
  const r = await fetch(`${base}/api/docs/${enc}/open?${params.toString()}`, { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
}

export interface LogEntry {
  ts: number;
  level: string;
  logger: string;
  message: string;
}

export async function fetchLogs(): Promise<LogEntry[]> {
  const r = await fetch(`${base}/api/logs`, noStore);
  if (!r.ok) throw new Error(await r.text());
  const j = await r.json();
  return j.logs ?? [];
}

export async function clearLogs(): Promise<void> {
  const r = await fetch(`${base}/api/logs`, { ...noStore, method: "DELETE" });
  if (!r.ok) throw new Error(await r.text());
}
