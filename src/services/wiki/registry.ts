import {
  dropEntry,
  isRegistryEntryReachable,
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
    .filter(isRegistryEntryReachable)
    .map(registeredWikiFromStore);
}

export async function dropRegisteredWiki(
  name: string,
): Promise<RegisteredWiki | null> {
  const removed = await dropEntry(name);
  return removed === null ? null : registeredWikiFromStore(removed);
}

function registeredWikiFromStore(entry: RegistryEntry): RegisteredWiki {
  return {
    name: entry.name,
    description: entry.description,
    path: entry.path,
    registered_at: entry.registered_at,
  };
}
