import { addWikiReviewItem } from "../../../../services/wiki/reviews.js";
import {
  reviewMarkdownInput,
  type ReviewMarkdownInput,
} from "./markdown.js";
import { renderReviewAddResult } from "./render/add.js";
import type { ReviewCommandOutput } from "./render/types.js";

export interface ReviewAddOptions extends ReviewMarkdownInput {
  cwd: string;
  wiki?: string;
  now?: Date;
  json?: boolean;
}

export async function runReviewAdd(
  options: ReviewAddOptions,
): Promise<ReviewCommandOutput> {
  return renderReviewAddResult(
    await addWikiReviewItem({
      cwd: options.cwd,
      wiki: options.wiki,
      markdown: reviewMarkdownInput(options),
      now: options.now,
    }),
    options.json,
  );
}
