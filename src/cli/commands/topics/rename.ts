import { renameWikiTopic } from "../../../services/wiki/topics.js";
import type { TopicsCommandOutput, TopicsRenameOptions } from "./types.js";

/**
 * `almanac topics rename <old> <new>`. Rewrites the slug both in
 * `topics.yaml` (as an entry key and in anyone who declared it as a
 * parent) and in every affected page's frontmatter.
 *
 * Refuses if `<new>` is already a distinct topic — "merging" two topics
 * should be explicit, not a silent side effect of a rename.
 */
export async function runTopicsRename(
  options: TopicsRenameOptions,
): Promise<TopicsCommandOutput> {
  const result = await renameWikiTopic({
    cwd: options.cwd,
    wiki: options.wiki,
    oldSlug: options.oldSlug,
    newSlug: options.newSlug,
  });

  switch (result.status) {
    case "renamed":
      return {
        stdout: `renamed ${result.oldSlug} → ${result.newSlug} (${result.pagesUpdated} page${result.pagesUpdated === 1 ? "" : "s"} updated)\n`,
        stderr: "",
        exitCode: 0,
      };
    case "unchanged":
      return {
        stdout: `topic "${result.slug}" unchanged\n`,
        stderr: "",
        exitCode: 0,
      };
    case "empty-slug":
      return { stdout: "", stderr: `almanac: empty topic slug\n`, exitCode: 1 };
    case "missing":
      return {
        stdout: "",
        stderr: `almanac: no such topic "${result.slug}"\n`,
        exitCode: 1,
      };
    case "already-exists":
      return {
        stdout: "",
        stderr: `almanac: topic "${result.slug}" already exists; delete it first if you intend to merge\n`,
        exitCode: 1,
      };
  }
}
