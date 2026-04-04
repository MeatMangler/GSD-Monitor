import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  fetchGroups,
  type GroupPayload,
  type SegmentPayload,
} from "./api";

type Ctx = {
  groups: GroupPayload[];
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  selectedGroupId: string | null;
  setSelectedGroupId: (id: string | null) => void;
  selectedSegmentKey: string | null;
  setSelectedSegmentKey: (k: string | null) => void;
  activeSegment: SegmentPayload | null;
  activeProject: SegmentPayload["project"] | null;
};

const AppCtx = createContext<Ctx | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [groups, setGroups] = useState<GroupPayload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [selectedSegmentKey, setSelectedSegmentKey] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const g = await fetchGroups();
      setGroups(g);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  useEffect(() => {
    if (!groups.length) {
      setSelectedGroupId(null);
      setSelectedSegmentKey(null);
      return;
    }
    setSelectedGroupId((id) => (id && groups.some((g) => g.id === id) ? id : groups[0].id));
  }, [groups]);

  useEffect(() => {
    const g = groups.find((x) => x.id === selectedGroupId);
    if (!g?.segments.length) {
      setSelectedSegmentKey(null);
      return;
    }
    setSelectedSegmentKey((prev) => {
      if (prev && g.segments.some((s) => s.segmentKey === prev)) return prev;
      const def =
        g.segments.find((s) => s.segmentKey === g.defaultSegmentKey) ?? g.segments[0];
      return def.segmentKey;
    });
  }, [groups, selectedGroupId]);

  useEffect(() => {
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/events`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as { type?: string };
        if (data.type === "projects_updated") {
          void reload();
        }
        // "settings_saved" events are intentionally ignored — no double reload on save
      } catch {
        // Non-JSON message; reload as fallback
        void reload();
      }
    };
    return () => ws.close();
  }, [reload]);

  const activeGroup = useMemo(
    () => groups.find((g) => g.id === selectedGroupId) ?? null,
    [groups, selectedGroupId],
  );

  const activeSegment = useMemo(() => {
    if (!activeGroup) return null;
    return (
      activeGroup.segments.find((s) => s.segmentKey === selectedSegmentKey) ??
      activeGroup.segments[0] ??
      null
    );
  }, [activeGroup, selectedSegmentKey]);

  const value: Ctx = {
    groups,
    loading,
    error,
    reload,
    selectedGroupId,
    setSelectedGroupId,
    selectedSegmentKey,
    setSelectedSegmentKey,
    activeSegment,
    activeProject: activeSegment?.project ?? null,
  };

  return <AppCtx.Provider value={value}>{children}</AppCtx.Provider>;
}

export function useApp() {
  const c = useContext(AppCtx);
  if (!c) throw new Error("useApp outside provider");
  return c;
}
