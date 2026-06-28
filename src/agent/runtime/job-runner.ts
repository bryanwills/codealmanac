import { createAgentRuntimeProviderRegistry } from "./providers/index.js";
import type { AgentRuntimeRunner } from "../../shared/agent-runtime/runner.js";

export function createAgentRuntimeJobRunner(args: {
  environment: NodeJS.ProcessEnv;
}): AgentRuntimeRunner {
  const registry = createAgentRuntimeProviderRegistry({
    environment: args.environment,
  });
  return async (spec, hooks) =>
    registry.getProvider(spec.provider.id).run(spec, hooks);
}
