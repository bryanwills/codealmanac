import { listJobRecords } from "../../stores/jobs/index.js";

export async function listJobProviderSessionIds(
  repoRoot: string,
): Promise<Set<string>> {
  const sessionIds = (await listJobRecords(repoRoot))
    .map((record) => record.providerSessionId)
    .filter((id): id is string => typeof id === "string" && id.length > 0);
  return new Set(sessionIds);
}
