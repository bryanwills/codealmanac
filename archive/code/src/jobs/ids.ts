import { randomBytes } from "node:crypto";

export function createJobId(now: Date = new Date()): string {
  const stamp = now
    .toISOString()
    .replace(/\D/g, "")
    .slice(0, 14);
  const suffix = randomBytes(4).toString("hex");
  return `job_${stamp}_${suffix}`;
}
