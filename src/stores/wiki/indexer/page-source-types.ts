import type { FrontmatterSource } from "./frontmatter-sources.js";

export interface IndexedPageSource {
  id: string;
  type: FrontmatterSource["type"];
  target: string;
  title?: string;
  retrieved_at?: string;
  note?: string;
  legacy: boolean;
}

export interface DerivedFileRef {
  rawPath: string;
  source: "structured-source" | "legacy-files";
}

export interface NormalizedPageSources {
  sources: IndexedPageSource[];
  fileRefs: DerivedFileRef[];
  hasLegacyFrontmatter: boolean;
  ambiguousLegacySources: string[];
}
