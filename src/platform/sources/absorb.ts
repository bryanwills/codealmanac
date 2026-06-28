import { resolveGitHubSource } from "../github/source.js";
import type { AbsorbInputSource } from "../../services/lifecycle/absorb/input-source.js";
import type { ResolveSourceFn } from "../../services/lifecycle/absorb/input.js";
import type { SourceRef, WebSourceRef } from "../../services/lifecycle/absorb/source-ref.js";

export function createPlatformAbsorbSourceResolver(): ResolveSourceFn {
  return (ref, cwd) => resolvePlatformAbsorbSource({ ref, cwd });
}

async function resolvePlatformAbsorbSource(args: {
  ref: SourceRef;
  cwd: string;
}): Promise<AbsorbInputSource> {
  if (args.ref.provider === "github") {
    return resolveGitHubSource({ ref: args.ref, cwd: args.cwd });
  }
  if (args.ref.provider === "web") return webInputSource(args.ref);

  const _exhaustive: never = args.ref;
  throw new Error(`unsupported source provider ${String(_exhaustive)}`);
}

function webInputSource(ref: WebSourceRef): AbsorbInputSource {
  return {
    kind: "web.url",
    raw: ref.raw,
    url: ref.url,
  };
}
