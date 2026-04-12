export function byLastUpdated(
  a: { last_updated?: string | null; number: number },
  b: { last_updated?: string | null; number: number },
): number {
  if (a.last_updated && b.last_updated) return b.last_updated.localeCompare(a.last_updated);
  if (a.last_updated) return -1;
  if (b.last_updated) return 1;
  return b.number - a.number;
}

export function fmtDate(d: string | null | undefined): string {
  if (!d) return "—";
  return new Date(d).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function statusLabel(s: string): string {
  switch (s) {
    case "in_progress":
      return "In progress";
    case "complete":
      return "Complete";
    case "needs_verification":
      return "Needs verification";
    default:
      return "Not started";
  }
}

export function statusBorderClass(status: string): string {
  switch (status) {
    case "complete":
      return "border-l-[#4ec994]";
    case "in_progress":
    case "needs_verification":
      return "border-l-[#007acc]";
    default:
      return "border-l-[#474747]";
  }
}
