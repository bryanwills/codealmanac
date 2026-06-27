import { BLUE, BOLD, DIM, RST } from "../../ansi.js";
import {
  dropRegisteredWiki,
  listReachableWikis,
  type RegisteredWiki,
} from "../../services/wiki/registry.js";

export interface ListOptions {
  json?: boolean;
  drop?: string;
  verbose?: boolean;
}

export interface ListCommandOutput {
  stdout: string;
  exitCode: number;
}

/**
 * `almanac list` — the global discovery surface. Three modes:
 *
 *  - default: reachable wiki names, one per line
 *  - `--verbose`: pretty table with descriptions and paths
 *  - `--json`: structured output (reachable wikis only, by default)
 *  - `--drop <name>`: explicit removal, then exits
 *
 * **Unreachable paths are silently skipped in the default output**, but
 * never auto-dropped. This is the registry hygiene rule from the design —
 * branch switches, unmounted drives, and VM-offline repos should not cost
 * the user a registration. Only `--drop` removes entries.
 */
export async function listWikis(
  options: ListOptions,
): Promise<ListCommandOutput> {
  if (options.drop !== undefined) {
    return handleDrop(options.drop);
  }

  const reachable = await listReachableWikis();

  if (options.json === true) {
    return { stdout: `${JSON.stringify(reachable, null, 2)}\n`, exitCode: 0 };
  }

  return {
    stdout: options.verbose === true
      ? formatPretty(reachable)
      : formatNames(reachable),
    exitCode: 0,
  };
}

async function handleDrop(name: string): Promise<ListCommandOutput> {
  const removed = await dropRegisteredWiki(name);
  if (removed === null) {
    return {
      stdout: `no registry entry named "${name}"\n`,
      exitCode: 1,
    };
  }
  return {
    stdout: `removed "${removed.name}" (${removed.path})\n`,
    exitCode: 0,
  };
}

/**
 * Human-readable listing. Empty state prints a gentle hint rather than a
 * blank screen, and entries render in registration order (chronological,
 * since `addEntry` appends).
 */
function formatPretty(entries: RegisteredWiki[]): string {
  if (entries.length === 0) {
    return `${DIM}no wikis registered. run \`almanac init\` in a repo to create one.${RST}\n`;
  }

  // Column-width the name for alignment; cap at 30 so absurd names don't
  // stretch the whole table.
  const nameWidth = Math.min(
    30,
    entries.reduce((w, e) => Math.max(w, e.name.length), 0),
  );

  const lines: string[] = [];
  for (const entry of entries) {
    const name = entry.name.padEnd(nameWidth);
    const desc = entry.description.length > 0 ? entry.description : "—";
    lines.push(`${BLUE}${BOLD}${name}${RST}  ${desc}`);
    lines.push(`${" ".repeat(nameWidth)}  ${DIM}${entry.path}${RST}`);
  }
  return `${lines.join("\n")}\n`;
}

function formatNames(entries: RegisteredWiki[]): string {
  if (entries.length === 0) return "";
  return `${entries.map((entry) => entry.name).join("\n")}\n`;
}
