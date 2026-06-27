import { readWikiTopic } from "../../../services/wiki/topics.js";
import { formatShow } from "./read.js";
import type { TopicsCommandOutput, TopicsShowOptions } from "./types.js";

/**
 * `almanac topics show <slug>`. Prints metadata + parents, children,
 * and the page list. `--descendants` widens the page list to include
 * pages tagged with any descendant topic (via the DAG).
 */
export async function runTopicsShow(
  options: TopicsShowOptions,
): Promise<TopicsCommandOutput> {
  const result = await readWikiTopic({
    cwd: options.cwd,
    wiki: options.wiki,
    slug: options.slug,
    descendants: options.descendants,
  });

  if (result.status === "empty-slug") {
    return {
      stdout: "",
      stderr: `almanac: empty topic slug\n`,
      exitCode: 1,
    };
  }

  if (result.status === "missing") {
    return {
      stdout: "",
      stderr: `almanac: no such topic "${result.slug}"\n`,
      exitCode: 1,
    };
  }

  if (options.json === true) {
    return {
      stdout: `${JSON.stringify(result.topic, null, 2)}\n`,
      stderr: "",
      exitCode: 0,
    };
  }
  return { stdout: formatShow(result.topic), stderr: "", exitCode: 0 };
}
