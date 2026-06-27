import { deleteWikiTopic } from "../../../services/wiki/topics.js";
import type { TopicsCommandOutput, TopicsDeleteOptions } from "./types.js";

/**
 * `almanac topics delete <slug>`. Removes the topic from `topics.yaml`
 * (if present), scrubs any parent edges pointing at it, and untags
 * every page that had it. Pages themselves are left alone — deleting a
 * topic doesn't delete pages, just the relationship.
 */
export async function runTopicsDelete(
  options: TopicsDeleteOptions,
): Promise<TopicsCommandOutput> {
  const result = await deleteWikiTopic({
    cwd: options.cwd,
    wiki: options.wiki,
    slug: options.slug,
  });

  switch (result.status) {
    case "deleted":
      return {
        stdout: `deleted topic "${result.slug}" (${result.pagesUpdated} page${result.pagesUpdated === 1 ? "" : "s"} untagged)\n`,
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
  }
}
