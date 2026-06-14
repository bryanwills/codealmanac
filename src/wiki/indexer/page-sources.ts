import type { FrontmatterSource } from "./frontmatter.js";
import { looksLikeDir, normalizePath } from "./paths.js";

export interface IndexedPageSource {
  id: string;
  type: FrontmatterSource["type"];
  target: string;
  title?: string;
  retrieved_at?: string;
  note?: string;
}

export interface DerivedFileRef {
  rawPath: string;
}

export interface NormalizedPageSources {
  sources: IndexedPageSource[];
  fileRefs: DerivedFileRef[];
}

export function normalizePageSources(input: {
  sources: FrontmatterSource[];
}): NormalizedPageSources {
  const sources: IndexedPageSource[] = [];
  const fileRefs: DerivedFileRef[] = [];

  for (const source of input.sources) {
    const indexed = sourceToIndexed(source);
    if (indexed === null) continue;
    sources.push(indexed);
    if (source.type === "file") {
      fileRefs.push({ rawPath: source.path });
    }
  }

  return { sources, fileRefs };
}

function sourceToIndexed(source: FrontmatterSource): IndexedPageSource | null {
  switch (source.type) {
    case "file":
      return optional({
        id: source.id,
        type: source.type,
        target: normalizeFileTarget(source.path),
        note: source.note,
      });
    case "web":
      return optional({
        id: source.id,
        type: source.type,
        target: source.url,
        title: source.title,
        retrieved_at: source.retrieved_at,
        note: source.note,
      });
    case "commit":
      return optional({
        id: source.id,
        type: source.type,
        target: source.rev,
        note: source.note,
      });
    case "pr":
    case "issue":
      return optional({
        id: source.id,
        type: source.type,
        target: source.url ?? source.number,
        note: source.note,
      });
    case "conversation":
      return optional({
        id: source.id,
        type: source.type,
        target: source.path ?? source.run_id,
        note: source.note,
      });
    case "wiki":
      return optional({
        id: source.id,
        type: source.type,
        target: source.slug,
        note: source.note,
      });
    case "manual":
      return {
        id: source.id,
        type: source.type,
        target: source.note,
        note: source.note,
      };
  }
}

function optional(
  source: Omit<IndexedPageSource, "target"> & { target?: string },
): IndexedPageSource | null {
  if (source.target === undefined || source.target.length === 0) return null;
  return {
    id: source.id,
    type: source.type,
    target: source.target,
    ...(source.title !== undefined ? { title: source.title } : {}),
    ...(source.retrieved_at !== undefined ? { retrieved_at: source.retrieved_at } : {}),
    ...(source.note !== undefined ? { note: source.note } : {}),
  };
}

function normalizeFileTarget(path: string): string {
  return normalizePath(path, looksLikeDir(path));
}
