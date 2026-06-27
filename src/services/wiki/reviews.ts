import { resolveWikiRoot } from "../../wiki/indexer/resolve-wiki.js";
import {
  loadReviewFile,
  nextReviewId,
  reviewYamlPath,
  summaryFromMarkdown,
  writeReviewFile,
  type ReviewFile,
  type ReviewItem,
  type ReviewStatus,
} from "../../stores/wiki-review/store.js";

export type { ReviewItem, ReviewStatus } from "../../stores/wiki-review/store.js";

export interface WikiReviewRequest {
  cwd: string;
  wiki?: string;
}

export interface AddWikiReviewItemRequest extends WikiReviewRequest {
  markdown?: string;
  now?: Date;
}

export interface ListWikiReviewItemsRequest extends WikiReviewRequest {
  status?: ReviewStatus | "all" | string;
}

export interface WikiReviewItemRequest extends WikiReviewRequest {
  id: string;
}

export interface ChangeWikiReviewItemRequest extends WikiReviewItemRequest {
  markdown?: string;
  now?: Date;
}

export type AddWikiReviewItemResult =
  | { status: "added"; item: ReviewItem }
  | { status: "missing-markdown" };

export type ListWikiReviewItemsResult =
  | { status: "listed"; items: ReviewItem[] }
  | { status: "invalid-status" };

export type GetWikiReviewItemResult =
  | { status: "found"; item: ReviewItem }
  | { status: "missing"; id: string };

export type DecideWikiReviewItemResult =
  | { status: "decided"; item: ReviewItem }
  | { status: "missing-markdown" }
  | { status: "missing"; id: string }
  | { status: "already-applied"; id: string };

export type ApplyWikiReviewItemResult =
  | { status: "applied"; item: ReviewItem }
  | { status: "missing-markdown" }
  | { status: "missing"; id: string }
  | { status: "not-decided"; id: string; currentStatus: ReviewStatus };

export type ReopenWikiReviewItemResult =
  | { status: "reopened"; item: ReviewItem }
  | { status: "missing"; id: string };

export async function addWikiReviewItem(
  request: AddWikiReviewItemRequest,
): Promise<AddWikiReviewItemResult> {
  const markdown = cleanMarkdown(request.markdown);
  if (markdown === null) return { status: "missing-markdown" };

  const { file, path } = await openReviewFile(request);
  const summary = summaryFromMarkdown(markdown);
  if (summary.length === 0) return { status: "missing-markdown" };

  const item: ReviewItem = {
    id: nextReviewId(summary, file.items),
    status: "open",
    summary,
    created_at: timestamp(request.now),
    body: markdown,
    decided_at: null,
    decision: null,
    applied_at: null,
    application: null,
  };
  file.items.push(item);
  await writeReviewFile(path, file);
  return { status: "added", item };
}

export async function listWikiReviewItems(
  request: ListWikiReviewItemsRequest,
): Promise<ListWikiReviewItemsResult> {
  const status = request.status ?? "open";
  if (!isReviewStatusFilter(status)) return { status: "invalid-status" };

  const { file } = await openReviewFile(request);
  const items = status === "all"
    ? file.items
    : file.items.filter((item) => item.status === status);
  return { status: "listed", items };
}

export async function getWikiReviewItem(
  request: WikiReviewItemRequest,
): Promise<GetWikiReviewItemResult> {
  const found = await findReviewItem(request);
  if (found === null) return { status: "missing", id: request.id };
  return { status: "found", item: found.item };
}

export async function decideWikiReviewItem(
  request: ChangeWikiReviewItemRequest,
): Promise<DecideWikiReviewItemResult> {
  const markdown = cleanMarkdown(request.markdown);
  if (markdown === null) return { status: "missing-markdown" };

  const found = await findReviewItem(request);
  if (found === null) return { status: "missing", id: request.id };
  const item = found.item;
  if (item.status === "applied") {
    return { status: "already-applied", id: item.id };
  }

  item.status = "decided";
  item.decision = markdown;
  item.decided_at = timestamp(request.now);
  item.applied_at = null;
  item.application = null;
  await writeReviewFile(found.path, found.file);
  return { status: "decided", item };
}

export async function applyWikiReviewItem(
  request: ChangeWikiReviewItemRequest,
): Promise<ApplyWikiReviewItemResult> {
  const markdown = cleanMarkdown(request.markdown);
  if (markdown === null) return { status: "missing-markdown" };

  const found = await findReviewItem(request);
  if (found === null) return { status: "missing", id: request.id };
  const item = found.item;
  if (item.status !== "decided") {
    return {
      status: "not-decided",
      id: item.id,
      currentStatus: item.status,
    };
  }

  item.status = "applied";
  item.application = markdown;
  item.applied_at = timestamp(request.now);
  await writeReviewFile(found.path, found.file);
  return { status: "applied", item };
}

export async function reopenWikiReviewItem(
  request: ChangeWikiReviewItemRequest,
): Promise<ReopenWikiReviewItemResult> {
  const found = await findReviewItem(request);
  if (found === null) return { status: "missing", id: request.id };

  const item = found.item;
  item.status = "open";
  item.reopened_at = timestamp(request.now);
  item.reopen_note = cleanMarkdown(request.markdown);
  item.decided_at = null;
  item.decision = null;
  item.applied_at = null;
  item.application = null;
  await writeReviewFile(found.path, found.file);
  return { status: "reopened", item };
}

interface OpenReviewFile {
  file: ReviewFile;
  path: string;
}

async function openReviewFile(request: WikiReviewRequest): Promise<OpenReviewFile> {
  const repoRoot = await resolveWikiRoot({
    cwd: request.cwd,
    wiki: request.wiki,
  });
  const path = reviewYamlPath(repoRoot);
  return { file: await loadReviewFile(path), path };
}

interface FoundReviewItem extends OpenReviewFile {
  item: ReviewItem;
}

async function findReviewItem(
  request: WikiReviewItemRequest,
): Promise<FoundReviewItem | null> {
  const opened = await openReviewFile(request);
  const item = opened.file.items.find((candidate) => candidate.id === request.id);
  return item === undefined ? null : { ...opened, item };
}

function cleanMarkdown(markdown: string | undefined): string | null {
  const input = markdown ?? "";
  if (input.trim().length === 0) return null;
  return input.replace(/\s+$/g, "");
}

function timestamp(now?: Date): string {
  return (now ?? new Date()).toISOString();
}

function isReviewStatusFilter(
  value: string,
): value is ReviewStatus | "all" {
  return (
    value === "open" ||
    value === "decided" ||
    value === "applied" ||
    value === "all"
  );
}
