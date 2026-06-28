import type { FrontmatterSource } from "./frontmatter-sources.js";
import { looksLikeDir, normalizePath } from "./paths.js";
import type { IndexedPageSource } from "./page-source-types.js";

export function structuredSourceToIndexed(
  source: FrontmatterSource,
  legacy: boolean,
): IndexedPageSource | null {
  switch (source.type) {
    case "file":
      return optional({
        id: source.id,
        type: source.type,
        target: normalizeFileSourceTarget(source.path),
        note: source.note,
        legacy,
      });
    case "web":
      return optional({
        id: source.id,
        type: source.type,
        target: source.url,
        title: source.title,
        retrieved_at: source.retrieved_at,
        note: source.note,
        legacy,
      });
    case "commit":
      return optional({
        id: source.id,
        type: source.type,
        target: source.rev,
        note: source.note,
        legacy,
      });
    case "pr":
    case "issue":
      return optional({
        id: source.id,
        type: source.type,
        target: source.url ?? source.number,
        note: source.note,
        legacy,
      });
    case "conversation":
      return optional({
        id: source.id,
        type: source.type,
        target: source.path ?? source.run_id,
        note: source.note,
        legacy,
      });
    case "wiki":
      return optional({
        id: source.id,
        type: source.type,
        target: source.slug,
        note: source.note,
        legacy,
      });
    case "manual":
      return {
        id: source.id,
        type: source.type,
        target: source.note,
        note: source.note,
        legacy,
      };
  }
}

export function normalizeFileSourceTarget(path: string): string {
  return normalizePath(path, looksLikeDir(path));
}

function optional(
  source: Omit<IndexedPageSource, "target"> & { target?: string },
): IndexedPageSource | null {
  if (source.target === undefined || source.target.length === 0) return null;
  return {
    id: source.id,
    type: source.type,
    target: source.target,
    legacy: source.legacy,
    ...(source.title !== undefined ? { title: source.title } : {}),
    ...(source.retrieved_at !== undefined ? { retrieved_at: source.retrieved_at } : {}),
    ...(source.note !== undefined ? { note: source.note } : {}),
  };
}
