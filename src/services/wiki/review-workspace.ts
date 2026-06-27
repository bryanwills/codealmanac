import { resolveWikiRoot } from "../../wiki/indexer/resolve-wiki.js";
import {
  loadReviewFile,
  reviewYamlPath,
  type ReviewFile,
  type ReviewItem,
} from "../../stores/wiki-review/store.js";
import type {
  WikiReviewItemRequest,
  WikiReviewRequest,
} from "./review-types.js";

export interface OpenWikiReviewFile {
  file: ReviewFile;
  path: string;
}

export interface FoundWikiReviewItem {
  file: ReviewFile;
  path: string;
  item: ReviewItem;
}

export async function openWikiReviewFile(
  request: WikiReviewRequest,
): Promise<OpenWikiReviewFile> {
  const repoRoot = await resolveWikiRoot({
    cwd: request.cwd,
    wiki: request.wiki,
  });
  const path = reviewYamlPath(repoRoot);
  return { file: await loadReviewFile(path), path };
}

export async function findWikiReviewItem(
  request: WikiReviewItemRequest,
): Promise<FoundWikiReviewItem | null> {
  const opened = await openWikiReviewFile(request);
  const item = opened.file.items.find((candidate) => candidate.id === request.id);
  return item === undefined
    ? null
    : {
        file: opened.file,
        path: opened.path,
        item,
      };
}
