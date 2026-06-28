import { basename, dirname } from "node:path/posix";

export function uniqueSourceId(base: string, used: Set<string>): string {
  const stem = base.length > 0 ? base : "source";
  let candidate = stem;
  let i = 2;
  while (used.has(candidate)) {
    candidate = `${stem}-${i}`;
    i++;
  }
  used.add(candidate);
  return candidate;
}

export function sourceIdFromPath(path: string): string {
  const withoutSlash = path.replace(/\/+$/, "");
  const leaf = basename(withoutSlash) || basename(dirname(withoutSlash));
  return kebab(leaf.replace(/\.[^.]+$/, ""));
}

export function sourceIdFromUrl(raw: string): string {
  try {
    const url = new URL(raw);
    const pathBits = url.pathname.split("/").filter((bit) => bit.length > 0);
    const last = pathBits[pathBits.length - 1] ?? "";
    const stem = last.replace(/\.[^.]+$/, "");
    return kebab(stem.length > 0 ? stem : url.hostname.replace(/^www\./, ""));
  } catch {
    return kebab(raw);
  }
}

export function isHttpUrl(raw: string): boolean {
  try {
    const url = new URL(raw);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

function kebab(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
