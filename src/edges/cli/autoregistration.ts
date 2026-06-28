import {
  autoRegisterIfNeeded,
} from "../../services/wiki/autoregistration.js";
import { pathsEqualOnCurrentPlatform } from "../../platform/path-case.js";
import type { RegistryEntry } from "../../stores/wiki-registry/index.js";

export function autoRegisterCurrentWikiIfNeeded(
  cwd: string,
): Promise<RegistryEntry | null> {
  return autoRegisterIfNeeded(cwd, {
    pathEquals: pathsEqualOnCurrentPlatform,
  });
}
