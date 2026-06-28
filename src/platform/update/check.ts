import type {
  UpdateLatestVersionRequest,
  UpdateLatestVersionResult,
} from "../../shared/update-runtime.js";

export interface FetchLatestVersionOptions extends UpdateLatestVersionRequest {
  fetchFn?: typeof fetch;
}

const REGISTRY_URL = "https://registry.npmjs.org/codealmanac";
const DEFAULT_TIMEOUT_MS = 3000;

export async function fetchLatestVersion(
  opts: FetchLatestVersionOptions = {},
): Promise<UpdateLatestVersionResult> {
  const timeoutMs = opts.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const fetchFn = opts.fetchFn ?? globalThis.fetch;

  try {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), timeoutMs);
    try {
      const res = await fetchFn(REGISTRY_URL, {
        signal: ac.signal,
        headers: { accept: "application/json" },
      });
      if (!res.ok) return { ok: false };

      const body = (await res.json()) as {
        ["dist-tags"]?: { latest?: unknown };
      };
      const latest = body["dist-tags"]?.latest;
      return typeof latest === "string" && latest.length > 0
        ? { ok: true, latest }
        : { ok: false };
    } finally {
      clearTimeout(timer);
    }
  } catch {
    return { ok: false };
  }
}
