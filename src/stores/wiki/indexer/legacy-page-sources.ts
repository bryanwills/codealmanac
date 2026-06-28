import {
  isHttpUrl,
  sourceIdFromPath,
  sourceIdFromUrl,
  uniqueSourceId,
} from "./page-source-ids.js";
import type { IndexedPageSource } from "./page-source-types.js";
import { normalizeFileSourceTarget } from "./structured-page-sources.js";

export interface LegacyPageSourceProjection {
  source: IndexedPageSource | null;
  ambiguousSource: string | null;
}

export function legacyFileSource(
  path: string,
  usedIds: Set<string>,
): IndexedPageSource {
  return {
    id: uniqueSourceId(sourceIdFromPath(path), usedIds),
    type: "file",
    target: normalizeFileSourceTarget(path),
    note: "Migrated from legacy files.",
    legacy: true,
  };
}

export function legacySourceString(
  raw: string,
  usedIds: Set<string>,
): LegacyPageSourceProjection {
  if (!isHttpUrl(raw)) {
    return { source: null, ambiguousSource: raw };
  }
  return {
    source: {
      id: uniqueSourceId(sourceIdFromUrl(raw), usedIds),
      type: "web",
      target: raw,
      note: "Migrated from legacy sources.",
      legacy: true,
    },
    ambiguousSource: null,
  };
}
