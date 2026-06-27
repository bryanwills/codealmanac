export interface WikiTopicSummary {
  slug: string;
  title: string | null;
  description: string | null;
  page_count: number;
  parents: string[];
}

export interface WikiTopicsRequest {
  cwd: string;
  wiki?: string;
}

export interface WikiTopicRequest {
  cwd: string;
  wiki?: string;
  slug: string;
  descendants?: boolean;
}

export interface DescribeWikiTopicRequest {
  cwd: string;
  wiki?: string;
  slug: string;
  description: string;
}

export interface CreateWikiTopicRequest {
  cwd: string;
  wiki?: string;
  name: string;
  parents?: string[];
}

export interface LinkWikiTopicsRequest {
  cwd: string;
  wiki?: string;
  child: string;
  parent: string;
}

export interface UnlinkWikiTopicsRequest {
  cwd: string;
  wiki?: string;
  child: string;
  parent: string;
}

export interface RenameWikiTopicRequest {
  cwd: string;
  wiki?: string;
  oldSlug: string;
  newSlug: string;
}

export interface DeleteWikiTopicRequest {
  cwd: string;
  wiki?: string;
  slug: string;
}

export interface WikiTopicRecord {
  slug: string;
  title: string;
  description: string | null;
  parents: string[];
  children: string[];
  pages: string[];
  descendants_used?: boolean;
}

export type WikiTopicResult =
  | { status: "found"; topic: WikiTopicRecord }
  | { status: "empty-slug" }
  | { status: "missing"; slug: string };

export type DescribeWikiTopicResult =
  | { status: "described"; slug: string }
  | { status: "empty-slug" }
  | { status: "missing"; slug: string };

export type CreateWikiTopicResult =
  | { status: "created"; slug: string }
  | { status: "updated"; slug: string }
  | { status: "invalid-name"; name: string }
  | { status: "self-parent" }
  | { status: "missing-parent"; parent: string }
  | { status: "cycle"; slug: string; parent: string };

export type LinkWikiTopicsResult =
  | { status: "linked"; child: string; parent: string }
  | { status: "already-exists"; child: string; parent: string }
  | { status: "empty-slug" }
  | { status: "self-parent" }
  | { status: "missing-topic"; slug: string }
  | { status: "cycle"; child: string; parent: string };

export type UnlinkWikiTopicsResult =
  | { status: "unlinked"; child: string; parent: string }
  | { status: "no-edge"; child: string; parent: string }
  | { status: "empty-slug" };

export type RenameWikiTopicResult =
  | {
      status: "renamed";
      oldSlug: string;
      newSlug: string;
      pagesUpdated: number;
    }
  | { status: "unchanged"; slug: string }
  | { status: "empty-slug" }
  | { status: "missing"; slug: string }
  | { status: "already-exists"; slug: string };

export type DeleteWikiTopicResult =
  | { status: "deleted"; slug: string; pagesUpdated: number }
  | { status: "empty-slug" }
  | { status: "missing"; slug: string };
