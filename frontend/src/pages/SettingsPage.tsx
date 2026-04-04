import { useEffect, useState } from "react";
import { browseFolders, fetchSettings, saveSettings, scanRootsFromSettings } from "../api";

export function SettingsPage() {
  const [roots, setRoots] = useState("");
  const [saving, setSaving] = useState(false);
  const [browsing, setBrowsing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    void fetchSettings().then((s) => {
      setRoots(scanRootsFromSettings(s).join("\n"));
    });
  }, []);

  async function save() {
    setSaving(true);
    setMessage(null);
    try {
      const list = roots
        .split("\n")
        .map((x) => x.trim())
        .filter(Boolean);
      await saveSettings({ scan_roots: list });
      const s = await fetchSettings();
      setRoots(scanRootsFromSettings(s).join("\n"));
      setMessage("Saved.");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  }

  async function addBrowse() {
    setBrowsing(true);
    setMessage(null);
    try {
      const { paths, cancelled } = await browseFolders();
      if (cancelled || paths.length === 0) return;
      const existing = roots
        .split("\n")
        .map((x) => x.trim())
        .filter(Boolean);
      const next = [...new Set([...existing, ...paths])];
      setRoots(next.join("\n"));
    } catch (e) {
      setMessage(e instanceof Error ? e.message : String(e));
    } finally {
      setBrowsing(false);
    }
  }

  return (
    <div className="p-6">
      <h2 className="mb-4 text-lg font-semibold text-white">Settings</h2>
      <p className="mb-2 text-sm text-zinc-500">
        One folder per line — parent directories that contain GSD repos or workspaces (including{" "}
        <code className="text-zinc-400">~/gsd-workspaces/...</code>).
      </p>
      <textarea
        className="mb-4 w-full max-w-xl rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 font-mono text-sm text-zinc-200"
        rows={8}
        value={roots}
        onChange={(e) => setRoots(e.target.value)}
        placeholder="D:\dev\my-repos"
      />
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          disabled={saving || browsing}
          className="rounded-md border border-zinc-600 bg-zinc-800 px-4 py-2 text-sm font-medium text-zinc-100 hover:bg-zinc-700 disabled:opacity-50"
          onClick={() => void addBrowse()}
        >
          {browsing ? "Browsing…" : "Browse…"}
        </button>
        <button
          type="button"
          disabled={saving || browsing}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
          onClick={() => void save()}
        >
          {saving ? "Saving…" : "Save"}
        </button>
        {message ? (
          <span className="text-sm text-zinc-400" role="status">
            {message}
          </span>
        ) : null}
      </div>
    </div>
  );
}
