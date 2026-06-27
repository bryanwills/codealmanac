/**
 * Tiny semver comparator for update-version checks. Almanac only needs a small
 * subset: numeric `major.minor.patch`, optional leading `v`, optional build
 * metadata, and a coarse pre-release ordering.
 */
interface ParsedVersion {
  major: number;
  minor: number;
  patch: number;
  /** Empty string = no pre-release, which is newer than a tag at the same triple. */
  pre: string;
}

function parseVersion(version: string): ParsedVersion | null {
  const trimmed = version.trim().replace(/^v/i, "");
  const noBuild = trimmed.split("+")[0] ?? "";
  const dashAt = noBuild.indexOf("-");
  const core = dashAt === -1 ? noBuild : noBuild.slice(0, dashAt);
  const pre = dashAt === -1 ? "" : noBuild.slice(dashAt + 1);

  const parts = core.split(".").map((part) => Number.parseInt(part, 10));
  if (parts.length === 0 || parts.some((part) => !Number.isFinite(part) || part < 0)) {
    return null;
  }
  return {
    major: parts[0] ?? 0,
    minor: parts[1] ?? 0,
    patch: parts[2] ?? 0,
    pre,
  };
}

export function isNewerVersion(latest: string, installed: string): boolean {
  const next = parseVersion(latest);
  const current = parseVersion(installed);
  if (next === null || current === null) return false;

  if (next.major !== current.major) return next.major > current.major;
  if (next.minor !== current.minor) return next.minor > current.minor;
  if (next.patch !== current.patch) return next.patch > current.patch;

  if (next.pre === current.pre) return false;
  if (next.pre === "" && current.pre !== "") return true;
  if (next.pre !== "" && current.pre === "") return false;
  return next.pre > current.pre;
}
