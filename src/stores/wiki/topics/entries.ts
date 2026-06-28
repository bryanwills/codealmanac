import { topicTitleFromSlug } from "./title.js";
import type { TopicEntry, TopicsFile } from "./types.js";

/**
 * Look up a topic by slug. Returns `null` when the slug is absent —
 * callers distinguish "declared in topics.yaml" from "ad-hoc (only
 * appears in page frontmatter)" based on this.
 */
export function findTopic(file: TopicsFile, slug: string): TopicEntry | null {
  for (const topic of file.topics) {
    if (topic.slug === slug) return topic;
  }
  return null;
}

/**
 * Ensure a topic entry exists. If missing, inserts a minimal entry with
 * title-cased title and null description. Returns the (possibly new)
 * entry. Used by `tag`, `topics create` (with `--parent auto-creating`),
 * and `topics link` (auto-creating child/parent on demand).
 */
export function ensureTopic(file: TopicsFile, slug: string): TopicEntry {
  const existing = findTopic(file, slug);
  if (existing !== null) return existing;

  const entry: TopicEntry = {
    slug,
    title: topicTitleFromSlug(slug),
    description: null,
    parents: [],
  };
  file.topics.push(entry);
  return entry;
}
