import { untagWikiPage } from "../../../../services/wiki/page-topic-mutations.js";
import { renderUntagResult, type TagCommandOutput } from "./render.js";

export interface UntagOptions {
  cwd: string;
  wiki?: string;
  page: string;
  topic: string;
}

export async function runUntag(
  options: UntagOptions,
): Promise<TagCommandOutput> {
  return renderUntagResult(await untagWikiPage(options));
}
