import { existsSync } from "node:fs";

import {
  dropEntry,
  readRegistry,
  type RegistryEntry,
} from "../../stores/wiki-registry/index.js";

export interface RegisteredWiki {
  name: string;
  description: string;
  path: string;
  registered_at: string;
}

export async function listReachableWikis(): Promise<RegisteredWiki[]> {
  const entries = await readRegistry();
  return entries
    .filter((entry) => isReachable(entry))
    .map(registeredWikiFromStore);
}

export async function dropRegisteredWiki(
  name: string,
): Promise<RegisteredWiki | null> {
  const removed = await dropEntry(name);
  return removed === null ? null : registeredWikiFromStore(removed);
}

/**
 * A registry path is reachable if something still exists at that path.
 * Unreachable entries stay in the registry until an explicit drop.
 */
function isReachable(entry: RegisteredWiki): boolean {
  if (entry.path.length === 0) return false;
  return existsSync(entry.path);
}

function registeredWikiFromStore(entry: RegistryEntry): RegisteredWiki {
  return {
    name: entry.name,
    description: entry.description,
    path: entry.path,
    registered_at: entry.registered_at,
  };
}
