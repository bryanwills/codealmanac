import { UserFacingError } from "../../shared/user-facing-error.js";
import { findNearestAlmanacDir } from "../../stores/wiki-files/repo-location.js";
import {
  findEntry,
  isRegistryEntryWikiRoot,
} from "../../stores/wiki-registry/index.js";

/**
 * Resolve the repo root a wiki command should target.
 *
 * `--wiki <name>` is explicit and loud: missing or unreachable named wikis are
 * user-facing errors. The implicit mode walks upward from `cwd`, like Git, and
 * asks the user to run `almanac init` when no enclosing wiki exists.
 */
export async function resolveWikiRoot(params: {
  cwd: string;
  wiki?: string;
}): Promise<string> {
  if (params.wiki !== undefined) {
    return resolveNamedWikiRoot(params.wiki);
  }

  const nearest = findNearestAlmanacDir(params.cwd);
  if (nearest !== null) return nearest;

  throw new UserFacingError(
    "no .almanac/ found in this directory or any parent",
    {
      outcome: "needs-action",
      fix: "run: almanac init",
    },
  );
}

async function resolveNamedWikiRoot(name: string): Promise<string> {
  const entry = await findEntry({ name });
  if (entry === null) {
    throw new UserFacingError(`no registered wiki named "${name}"`, {
      data: { wiki: name },
    });
  }
  if (!isRegistryEntryWikiRoot(entry)) {
    throw new UserFacingError(
      `wiki "${name}" path is unreachable (${entry.path})`,
      { data: { wiki: name, path: entry.path } },
    );
  }
  return entry.path;
}
