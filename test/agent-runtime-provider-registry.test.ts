import { describe, expect, it } from "vitest";

import {
  createAgentRuntimeProviderRegistry,
  AGENT_RUNTIME_PROVIDER_METADATA,
} from "../src/agent/runtime/index.js";

describe("agent runtime provider registry", () => {
  it("lists the supported provider ids", () => {
    const registry = createAgentRuntimeProviderRegistry({ environment: {} });

    expect(registry.listProviders().map((provider) => provider.metadata.id)).toEqual([
      "claude",
      "codex",
      "cursor",
    ]);
  });

  it("returns provider metadata by id", () => {
    const registry = createAgentRuntimeProviderRegistry({ environment: {} });

    expect(registry.getProvider("claude").metadata).toBe(
      AGENT_RUNTIME_PROVIDER_METADATA.claude,
    );
    expect(registry.getProvider("codex").metadata.displayName).toBe("Codex");
    expect(registry.getProvider("cursor").metadata.displayName).toBe("Cursor");
  });

  it("keeps capability differences explicit", () => {
    expect(
      AGENT_RUNTIME_PROVIDER_METADATA.claude.capabilities.subagents.programmaticPerRun,
    ).toBe(true);
    expect(
      AGENT_RUNTIME_PROVIDER_METADATA.codex.capabilities.subagents.programmaticPerRun,
    ).toBe(false);
    expect(AGENT_RUNTIME_PROVIDER_METADATA.codex.capabilities.subagents.supported).toBe(false);
    expect(AGENT_RUNTIME_PROVIDER_METADATA.codex.capabilities.sessionPersistence).toBe(false);
    expect(AGENT_RUNTIME_PROVIDER_METADATA.codex.capabilities.reasoningEffort).toBe(true);
    expect(AGENT_RUNTIME_PROVIDER_METADATA.codex.capabilities.contextUsage).toBe(true);
    expect(AGENT_RUNTIME_PROVIDER_METADATA.cursor.capabilities.fileWrite).toBe(false);
    expect(AGENT_RUNTIME_PROVIDER_METADATA.claude.capabilities.contextUsage).toBe(false);
    expect(AGENT_RUNTIME_PROVIDER_METADATA.claude.capabilities.structuredOutput).toBe(true);
  });

  it("keeps unported adapters explicit", async () => {
    const registry = createAgentRuntimeProviderRegistry({ environment: {} });

    await expect(
      registry.getProvider("cursor").run({
        provider: { id: "cursor" },
        cwd: "/repo",
        prompt: "hello",
        metadata: { operation: "build" },
      }),
    ).resolves.toMatchObject({
      success: false,
      error: expect.stringContaining("not implemented yet"),
    });
  });
});
