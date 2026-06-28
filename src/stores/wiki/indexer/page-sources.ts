import type { FrontmatterSource } from "./frontmatter-sources.js";
import {
  legacyFileSource,
  legacySourceString,
} from "./legacy-page-sources.js";
import type {
  DerivedFileRef,
  IndexedPageSource,
  NormalizedPageSources,
} from "./page-source-types.js";
import { structuredSourceToIndexed } from "./structured-page-sources.js";

export function normalizePageSources(input: {
  sources: FrontmatterSource[];
  legacyFiles: string[];
  legacySourceStrings: string[];
}): NormalizedPageSources {
  const usedIds = new Set(input.sources.map((source) => source.id));
  const sources: IndexedPageSource[] = [];
  const fileRefs: DerivedFileRef[] = [];
  const ambiguousLegacySources: string[] = [];

  for (const source of input.sources) {
    const indexed = structuredSourceToIndexed(source, false);
    if (indexed === null) continue;
    sources.push(indexed);
    if (source.type === "file") {
      fileRefs.push({ rawPath: source.path, source: "structured-source" });
    }
  }

  for (const path of input.legacyFiles) {
    sources.push(legacyFileSource(path, usedIds));
    fileRefs.push({ rawPath: path, source: "legacy-files" });
  }

  for (const raw of input.legacySourceStrings) {
    const legacy = legacySourceString(raw, usedIds);
    if (legacy.ambiguousSource !== null) {
      ambiguousLegacySources.push(legacy.ambiguousSource);
      continue;
    }
    if (legacy.source !== null) sources.push(legacy.source);
  }

  return {
    sources,
    fileRefs,
    hasLegacyFrontmatter:
      input.legacyFiles.length > 0 || input.legacySourceStrings.length > 0,
    ambiguousLegacySources,
  };
}
