import { looksLikeDir, normalizePath } from "../indexer/paths.js";

export interface FileMentionFilter {
  isDir: boolean;
  normalizedPath: string;
  globPrefix: string;
  parentFolders: string[];
}

export function buildFileMentionFilter(input: string): FileMentionFilter {
  const isDir = looksLikeDir(input);
  const normalizedPath = normalizePath(input, isDir);
  return {
    isDir,
    normalizedPath,
    globPrefix: `${escapeGlobMeta(normalizedPath)}*`,
    parentFolders: isDir ? [] : parentFolderPrefixes(normalizedPath),
  };
}

/**
 * For a normalized file path like `src/checkout/handler.ts`, enumerate
 * every containing folder in stored form: `['src/', 'src/checkout/']`.
 */
export function parentFolderPrefixes(filePath: string): string[] {
  const out: string[] = [];
  let cursor = 0;
  while (true) {
    const next = filePath.indexOf("/", cursor);
    if (next === -1) break;
    out.push(filePath.slice(0, next + 1));
    cursor = next + 1;
  }
  return out;
}

export function escapeGlobMeta(input: string): string {
  return input.replace(/[\*\?\[]/g, (ch) => `[${ch}]`);
}

export function appendFileMentionClause(
  whereClauses: string[],
  params: (string | number)[],
  input: string,
): void {
  const mention = buildFileMentionFilter(input);
  if (mention.isDir) {
    // Folder queries need GLOB for prefix matching, but the pattern is built
    // from the user query after escaping GLOB metacharacters. Never concatenate
    // stored file_refs paths into a GLOB pattern: Next.js-style paths such as
    // `src/[id]/page.tsx` must stay literal.
    whereClauses.push(
      `EXISTS (
         SELECT 1 FROM file_refs r
         WHERE r.page_slug = p.slug
           AND (r.path = ? OR r.path GLOB ?)
       )`,
    );
    params.push(mention.normalizedPath, mention.globPrefix);
    return;
  }

  // File queries match the exact file plus any containing folder refs. Use
  // equality over enumerated parent folders instead of GLOB over stored values
  // so metacharacters in stored paths remain literal.
  if (mention.parentFolders.length === 0) {
    whereClauses.push(
      `EXISTS (
         SELECT 1 FROM file_refs r
         WHERE r.page_slug = p.slug AND r.path = ?
       )`,
    );
    params.push(mention.normalizedPath);
    return;
  }

  const placeholders = mention.parentFolders.map(() => "?").join(", ");
  whereClauses.push(
    `EXISTS (
       SELECT 1 FROM file_refs r
       WHERE r.page_slug = p.slug
         AND (
           r.path = ?
           OR (r.is_dir = 1 AND r.path IN (${placeholders}))
         )
     )`,
  );
  params.push(mention.normalizedPath, ...mention.parentFolders);
}
