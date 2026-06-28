export function firstMeaningfulLine(text: string | undefined): string | null {
  if (text === undefined) return null;
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.replace(/^#+\s*/, "").trim();
    if (line.length === 0 || line === "---") continue;
    return line;
  }
  return null;
}

export function truncate(value: string, max: number): string {
  return value.length > max ? `${value.slice(0, max - 3)}...` : value;
}
