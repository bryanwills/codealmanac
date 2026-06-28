/**
 * One entry in `.almanac/topics.yaml` — the source of truth for topic
 * metadata (title, description, DAG parents). Pages are still the source
 * of truth for which pages belong to which topics; this file only holds
 * the topic-level attributes.
 *
 * `slug` is the canonical kebab-case key used everywhere downstream
 * (SQLite `topics.slug`, page frontmatter `topics:` entries, wikilink
 * targets). `title` is the human-readable name the user typed at create
 * time. `description` is a free-form one-liner (or null when unset).
 * `parents` is the DAG edge list — kept as an array of slugs rather than
 * a nested structure so round-tripping stays boring and a user eyeballing
 * the file can see the full graph.
 */
export interface TopicEntry {
  slug: string;
  title: string;
  description: string | null;
  parents: string[];
}

export interface TopicsFile {
  topics: TopicEntry[];
}
