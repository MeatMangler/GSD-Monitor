import type { ReactNode } from "react";

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children?: ReactNode;
}

export function Drawer({ open, onClose, title, children }: DrawerProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <aside className="relative flex w-[480px] flex-col border-l border-[#474747] bg-[#1e1e1e] overflow-y-auto">
        <div className="flex items-center justify-between border-b border-[#474747] px-4 py-3">
          <h2 className="font-mono text-sm font-medium text-[#cccccc]">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-[#858585] hover:text-[#cccccc]"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 text-sm text-[#cccccc]">
          {children}
        </div>
      </aside>
    </div>
  );
}
