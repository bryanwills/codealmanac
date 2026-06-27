/**
 * Parse a compact duration string of the form `<N><unit>` into seconds.
 *
 * Accepted units (from the spec, `--since` / `--stale`):
 *   - `s` — seconds
 *   - `m` — minutes
 *   - `h` — hours
 *   - `d` — days
 *   - `w` — weeks
 *
 * Examples: `2w` → 1209600, `30d` → 2592000, `12h` → 43200.
 *
 * Anything else throws — the CLI surfaces the error with the usual
 * `almanac: <message>` prefix, which is clearer than silently treating
 * `2weeks` or `30 days` as zero.
 */
export function parseDuration(input: string): number {
  const trimmed = input.trim();
  const m = trimmed.match(/^(\d+)([smhdw])$/);
  if (m === null) {
    throw new Error(
      `invalid duration "${input}" (expected Ns, Nm, Nh, Nd, or Nw — e.g. 30s, 45m, 2w)`,
    );
  }
  const n = Number.parseInt(m[1] ?? "0", 10);
  const unit = m[2];
  switch (unit) {
    case "s":
      return n;
    case "m":
      return n * 60;
    case "h":
      return n * 60 * 60;
    case "d":
      return n * 60 * 60 * 24;
    case "w":
      return n * 60 * 60 * 24 * 7;
    default:
      // Unreachable — regex pins the unit — but satisfies exhaustiveness.
      throw new Error(`invalid duration unit "${unit ?? ""}"`);
  }
}

export function formatDuration(ms: number): string {
  if (ms < 0) return "just now";
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 48) return `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days}d`;
}
