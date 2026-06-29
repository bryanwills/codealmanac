import { readCredentials, login } from "../../../cloud/auth.js";
import { installClaudeCloudHooks } from "../../../platform/cloud-hooks/claude.js";
import { installCodexCloudHooks } from "../../../platform/cloud-hooks/codex.js";
import { BAR, stepDone } from "./output.js";

export interface CloudCaptureSetupOptions {
  cloudHooksHomeDir?: string;
  codexCloudHooksPath?: string;
  claudeCloudHooksPath?: string;
  ensureCloudLogin?: () => Promise<void>;
}

export async function runCloudCaptureSetupStep(args: {
  out: NodeJS.WritableStream;
  options: CloudCaptureSetupOptions;
}): Promise<void> {
  await (args.options.ensureCloudLogin ?? ensureCloudLogin)();
  stepDone(args.out, "Signed in to Almanac Cloud");
  await Promise.all([
    installCodexCloudHooks({
      homeDir: args.options.cloudHooksHomeDir,
      configPath: args.options.codexCloudHooksPath,
    }),
    installClaudeCloudHooks({
      homeDir: args.options.cloudHooksHomeDir,
      configPath: args.options.claudeCloudHooksPath,
    }),
  ]);
  stepDone(args.out, "Cloud capture ready (Claude + Codex)");
  args.out.write(BAR + "\n");
}

async function ensureCloudLogin(): Promise<void> {
  const credentials = await readCredentials();
  if (credentials !== null) return;
  await login();
}
