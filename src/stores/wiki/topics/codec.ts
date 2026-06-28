import yaml from "js-yaml";

import { toKebabCase } from "../../../shared/slug.js";
import { UserFacingError } from "../../../shared/user-facing-error.js";
import { topicTitleFromSlug } from "./title.js";
import type { TopicEntry, TopicsFile } from "./types.js";

export function parseTopicsFileContent(
  raw: string,
  path: string,
): TopicsFile {
  const trimmed = raw.trim();
  if (trimmed.length === 0) {
    return { topics: [] };
  }

  let parsed: unknown;
  try {
    parsed = yaml.load(raw);
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    throw new UserFacingError(
      `topics.yaml at ${path} is not valid YAML: ${message}`,
      { data: { path } },
    );
  }

  if (parsed === null || parsed === undefined) {
    return { topics: [] };
  }

  if (typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new UserFacingError(`topics.yaml at ${path} must be a mapping`, {
      data: { path },
    });
  }

  const obj = parsed as Record<string, unknown>;
  const rawTopics = obj.topics;
  if (rawTopics === undefined || rawTopics === null) {
    return { topics: [] };
  }
  if (!Array.isArray(rawTopics)) {
    throw new UserFacingError(
      `topics.yaml at ${path} — "topics" must be a list`,
      { data: { path, field: "topics" } },
    );
  }

  return { topics: rawTopics.flatMap(normalizeTopicEntry) };
}

export function formatTopicsFileContent(file: TopicsFile): string {
  const sorted = [...file.topics].sort((a, b) => a.slug.localeCompare(b.slug));
  const doc = {
    topics: sorted.map((topic) => ({
      slug: topic.slug,
      title: topic.title,
      description: topic.description,
      parents: topic.parents,
    })),
  };

  const header =
    `# .almanac/topics.yaml — source of truth for topic metadata.\n` +
    `# Managed by \`almanac topics\` commands. User-added comments\n` +
    `# between entries will be stripped on the next write (js-yaml\n` +
    `# doesn't round-trip comments). Edit at your own risk — or use the\n` +
    `# CLI (\`almanac topics create|link|describe|rename|delete\`)\n` +
    `# which preserves the structure correctly.\n`;
  const body = yaml.dump(doc, {
    lineWidth: 100,
    noRefs: true,
    sortKeys: false,
  });
  return `${header}${body}`;
}

function normalizeTopicEntry(item: unknown): TopicEntry[] {
  if (typeof item !== "object" || item === null || Array.isArray(item)) {
    return [];
  }

  const entry = item as Record<string, unknown>;
  const slugRaw = entry.slug;
  if (typeof slugRaw !== "string" || slugRaw.trim().length === 0) {
    return [];
  }

  const slug = toKebabCase(slugRaw);
  if (slug.length === 0) {
    return [];
  }

  return [
    {
      slug,
      title: normalizeTopicTitle(entry.title, slug),
      description: normalizeTopicDescription(entry.description),
      parents: normalizeTopicParents(entry.parents, slug),
    },
  ];
}

function normalizeTopicTitle(value: unknown, slug: string): string {
  if (typeof value === "string" && value.trim().length > 0) {
    return value.trim();
  }
  return topicTitleFromSlug(slug);
}

function normalizeTopicDescription(value: unknown): string | null {
  if (typeof value === "string" && value.trim().length > 0) {
    return value.trim();
  }
  return null;
}

function normalizeTopicParents(value: unknown, slug: string): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const parents: string[] = [];
  for (const parent of value) {
    if (typeof parent !== "string" || parent.trim().length === 0) {
      continue;
    }
    const parentSlug = toKebabCase(parent);
    if (
      parentSlug.length > 0 &&
      parentSlug !== slug &&
      !parents.includes(parentSlug)
    ) {
      parents.push(parentSlug);
    }
  }
  return parents;
}
