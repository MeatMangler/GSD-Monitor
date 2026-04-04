import { useApp } from "../context";

export function DocsPage() {
  const { activeSegment } = useApp();

  if (!activeSegment) {
    return (
      <div className="p-6 text-[#858585] text-sm">
        Add scan roots in Settings and select a project.
      </div>
    );
  }

  return (
    <div className="p-6 text-[#858585] text-sm">
      Doc browser loading...
    </div>
  );
}
