import { tagWikiPages } from "../../../../services/wiki/page-topic-mutations.js";
import { renderTagResult, type TagCommandOutput } from "./render.js";

export interface TagOptions {
  cwd: string;
  wiki?: string;
  page?: string;
  topics: string[];
  stdin?: boolean;
  stdinInput?: string;
}

export async function runTag(options: TagOptions): Promise<TagCommandOutput> {
  return renderTagResult(await tagWikiPages(options));
}
