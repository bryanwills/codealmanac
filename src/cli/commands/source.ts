import type { CommandResult } from "../helpers.js";
import { renderOutcome } from "../outcome.js";
import {
  readGitHubSource,
  type GitHubSourceObjectKind,
  type ReadGitHubSourceOptions,
} from "../../connectors/github/source.js";

export interface SourceGitHubOptions
  extends Omit<ReadGitHubSourceOptions, "kind" | "number" | "repo"> {
  kind: GitHubSourceObjectKind;
  number: string;
  repo?: string;
  json?: boolean;
}

export async function runSourceGitHub(
  options: SourceGitHubOptions,
): Promise<CommandResult> {
  if (options.repo === undefined || options.repo.length === 0) {
    return renderOutcome(
      { type: "error", message: "--repo owner/repo is required" },
      { json: options.json },
    );
  }
  try {
    const result = await readGitHubSource({
      ...options,
      repo: options.repo,
    });
    return {
      stdout: `${JSON.stringify(result, null, 2)}\n`,
      stderr: "",
      exitCode: 0,
    };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    const isSetup =
      message.includes("Composio") ||
      message.includes("GitHub connector account");
    return renderOutcome(
      isSetup
        ? {
            type: "needs-action",
            message,
            fix: "run: almanac connect github",
          }
        : { type: "error", message },
      { json: options.json },
    );
  }
}
