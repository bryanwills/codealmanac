import type {
  AgentRuntimeProvider,
  ProviderMetadata,
  ProviderStatus,
} from "../types.js";
import type { OperationSpec } from "../../../operations/spec.js";

export function createNotImplementedProvider(
  metadata: ProviderMetadata,
): AgentRuntimeProvider {
  return {
    metadata,
    checkStatus: async (): Promise<ProviderStatus> => ({
      id: metadata.id,
      installed: false,
      authenticated: false,
      detail: `${metadata.displayName} agent runtime adapter is not implemented yet`,
    }),
    run: async (spec: OperationSpec) => ({
      success: false,
      result: "",
      error:
        `${metadata.displayName} agent runtime adapter is not implemented yet ` +
        `for ${spec.metadata?.operation ?? "unknown"} runs`,
    }),
  };
}
