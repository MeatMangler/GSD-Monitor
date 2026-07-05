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
  refreshGroups,
  type GroupPayload,
  type SegmentPayload,
} from "./api";

type Ctx = {
  groups: GroupPayload[];
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  forceRefresh: () => Promise<void>;
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

  const forceRefresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const g = await refreshGroups();
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
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let destroyed = false;
    let attempt = 0;

    function connect() {
      if (destroyed) return;
      const proto = window.location.protocol === "https:" ? "wss" : "ws";
      ws = new WebSocket(`${proto}://${window.location.host}/ws/events`);

      ws.onmessage = (event) => {
        attempt = 0; // Reset backoff on successful message
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

      ws.onopen = () => {
        attempt = 0; // Reset backoff on successful connection
        void reload(); // Catch any broadcast missed during connect race
      };

      ws.onclose = () => {
        ws = null;
        if (destroyed) return;
        // Exponential backoff: 1s, 2s, 4s, 8s, 16s, capped at 30s
        const delay = Math.min(1000 * Math.pow(2, attempt), 30_000);
        attempt += 1;
        reconnectTimer = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        // onclose will fire after onerror; reconnect is handled there
        ws?.close();
      };
    }

    connect();

    return () => {
      destroyed = true;
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      ws?.close();
    };
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
    forceRefresh,
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
