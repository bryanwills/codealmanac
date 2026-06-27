import { describeWikiTopic } from "../../../services/wiki/topics.js";
import type { TopicsCommandOutput, TopicsDescribeOptions } from "./types.js";

/**
 * `almanac topics describe <slug> "<text>"`. Sets or updates the
 * one-liner description. An empty string clears it.
 */
export async function runTopicsDescribe(
  options: TopicsDescribeOptions,
): Promise<TopicsCommandOutput> {
  const result = await describeWikiTopic({
    cwd: options.cwd,
    wiki: options.wiki,
    slug: options.slug,
    description: options.description,
  });

  if (result.status === "empty-slug") {
    return { stdout: "", stderr: `almanac: empty topic slug\n`, exitCode: 1 };
  }

  if (result.status === "missing") {
    return {
      stdout: "",
      stderr: `almanac: no such topic "${result.slug}"\n`,
      exitCode: 1,
    };
  }

  return {
    stdout: `described ${result.slug}\n`,
    stderr: "",
    exitCode: 0,
  };
}
