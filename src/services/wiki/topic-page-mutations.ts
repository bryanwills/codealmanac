import { toKebabCase } from "../../shared/slug.js";
import { runIndexer } from "../../stores/wiki/indexer/index.js";
import { resolveWikiRoot } from "./wiki-root.js";
import { topicsYamlPath } from "../../stores/wiki/topics/paths.js";
import { topicTitleFromSlug } from "../../stores/wiki/topics/title.js";
import {
  findTopic,
  writeTopicsFile,
} from "../../stores/wiki/topics/yaml.js";
import type {
  DeleteWikiTopicRequest,
  DeleteWikiTopicResult,
  RenameWikiTopicRequest,
  RenameWikiTopicResult,
} from "./topic-types.js";
import { rewriteTopicOnPages } from "../../stores/wiki/topics/page-rewrite.js";
import {
  openEditableTopicWorkspace,
  topicExists,
} from "./topic-workspace.js";

export async function renameWikiTopic(
  request: RenameWikiTopicRequest,
): Promise<RenameWikiTopicResult> {
  const repoRoot = await resolveWikiRoot({
    cwd: request.cwd,
    wiki: request.wiki,
  });
  const oldSlug = toKebabCase(request.oldSlug);
  const newSlug = toKebabCase(request.newSlug);
  if (oldSlug.length === 0 || newSlug.length === 0) {
    return { status: "empty-slug" };
  }
  if (oldSlug === newSlug) return { status: "unchanged", slug: oldSlug };

  const { file, db } = await openEditableTopicWorkspace(repoRoot);
  let pagesUpdated: number;
  try {
    const oldInYaml = findTopic(file, oldSlug);
    if (!topicExists(file, db, oldSlug)) {
      return { status: "missing", slug: oldSlug };
    }

    if (topicExists(file, db, newSlug)) {
      return { status: "already-exists", slug: newSlug };
    }

    if (oldInYaml !== null) {
      oldInYaml.slug = newSlug;
      if (oldInYaml.title === topicTitleFromSlug(oldSlug)) {
        oldInYaml.title = topicTitleFromSlug(newSlug);
      }
    }
    for (const topic of file.topics) {
      topic.parents = topic.parents.map((parent) =>
        parent === oldSlug ? newSlug : parent,
      );
    }

    await writeTopicsFile(topicsYamlPath(repoRoot), file);
    pagesUpdated = await rewriteTopicOnPages(repoRoot, (topics) =>
      topics.map((topic) => (topic === oldSlug ? newSlug : topic)),
    );
  } finally {
    db.close();
  }

  await runIndexer({ repoRoot });
  return { status: "renamed", oldSlug, newSlug, pagesUpdated };
}

export async function deleteWikiTopic(
  request: DeleteWikiTopicRequest,
): Promise<DeleteWikiTopicResult> {
  const repoRoot = await resolveWikiRoot({
    cwd: request.cwd,
    wiki: request.wiki,
  });
  const slug = toKebabCase(request.slug);
  if (slug.length === 0) return { status: "empty-slug" };

  const { file, db } = await openEditableTopicWorkspace(repoRoot);
  let pagesUpdated: number;
  try {
    if (!topicExists(file, db, slug)) {
      return { status: "missing", slug };
    }

    file.topics = file.topics.filter((topic) => topic.slug !== slug);
    for (const topic of file.topics) {
      topic.parents = topic.parents.filter((parent) => parent !== slug);
    }

    await writeTopicsFile(topicsYamlPath(repoRoot), file);
    pagesUpdated = await rewriteTopicOnPages(repoRoot, (topics) =>
      topics.filter((topic) => topic !== slug),
    );
  } finally {
    db.close();
  }

  await runIndexer({ repoRoot });
  return { status: "deleted", slug, pagesUpdated };
}
