import { buildLaunchPath, type LaunchdJobDefinition } from "./launchd.js";
import { automationLogPaths, launchAgentPlistPath } from "./paths.js";

export type AutomationSchedulerJob = LaunchdJobDefinition;

export interface AutomationSchedulerJobInput {
  home: string;
  label: string;
  plistPath?: string;
  pathEnvironment?: string;
  programArguments: string[];
  intervalSeconds: number;
  stdoutLogName: string;
  stderrLogName: string;
  workingDirectory?: string;
}

export function buildAutomationSchedulerJob(
  input: AutomationSchedulerJobInput,
): AutomationSchedulerJob {
  const logs = automationLogPaths({
    home: input.home,
    stdoutLogName: input.stdoutLogName,
    stderrLogName: input.stderrLogName,
  });

  return {
    plistPath: automationSchedulerPlistPath(input),
    label: input.label,
    programArguments: input.programArguments,
    intervalSeconds: input.intervalSeconds,
    environmentVariables: {
      PATH: buildLaunchPath(input.home, input.pathEnvironment),
    },
    workingDirectory: input.workingDirectory,
    stdoutPath: logs.stdoutPath,
    stderrPath: logs.stderrPath,
  };
}

export function automationSchedulerPlistPath(args: {
  home: string;
  label: string;
  plistPath?: string;
}): string {
  return args.plistPath ?? launchAgentPlistPath(args.label, args.home);
}
