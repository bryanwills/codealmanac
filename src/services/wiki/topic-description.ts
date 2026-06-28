import { toKebabCase } from "../../shared/slug.js";
import { runIndexer } from "../../stores/wiki/indexer/index.js";
import * as query from "../../stores/wiki/query/index.js";
import { ensureTopic } from "../../stores/wiki/topics/entries.js";
import { topicsYamlPath } from "../../stores/wiki/topics/paths.js";
import {
  loadTopicsFile,
  writeTopicsFile,
} from "../../stores/wiki/topics/yaml.js";
import type {
  DescribeWikiTopicRequest,
  DescribeWikiTopicResult,
} from "./topic-types.js";
import { openFreshTopicIndex } from "./topic-workspace.js";

export async function describeWikiTopic(
  request: DescribeWikiTopicRequest,
): Promise<DescribeWikiTopicResult> {
  const slug = toKebabCase(request.slug);
  if (slug.length === 0) return { status: "empty-slug" };

  const { repoRoot, db } = await openFreshTopicIndex(request);
  try {
    const detail = query.topics.topicDetail(db, slug);
    if (detail === null) return { status: "missing", slug };

    const yamlPath = topicsYamlPath(repoRoot);
    const file = await loadTopicsFile(yamlPath);
    const entry = ensureTopic(file, slug);
    const text = request.description.trim();
    entry.description = text.length === 0 ? null : text;

    await writeTopicsFile(yamlPath, file);
  } finally {
    db.close();
  }

  await runIndexer({ repoRoot });
  return { status: "described", slug };
}
