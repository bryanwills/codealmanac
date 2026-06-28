import { describe, expect, it } from "vitest";

import { createAbsorbRunSpec } from "../src/services/lifecycle/operations/absorb.js";
import { createBuildRunSpec } from "../src/services/lifecycle/operations/build.js";
import { createGardenRunSpec } from "../src/services/lifecycle/operations/garden.js";
import { createOperationRunSpec } from "../src/services/lifecycle/operations/run.js";
import type { OperationPromptLoader } from "../src/shared/operation-prompts.js";

const TEST_PROMPT_LOADER: OperationPromptLoader = async (name) => `${name} prompt`;

describe("operation run defaults", () => {
  it("uses Codex 5.5 when a caller does not pass a provider", async () => {
    const spec = await createOperationRunSpec({
      operation: "garden",
      promptName: "operations/garden",
      repoRoot: "/repo",
      loadPrompt: TEST_PROMPT_LOADER,
    });

    expect(spec.provider).toEqual({ id: "codex", model: "gpt-5.5" });
  });

  it("uses Codex 5.5 for every operation-specific spec helper", async () => {
    const build = await createBuildRunSpec({
      repoRoot: "/repo",
      loadPrompt: TEST_PROMPT_LOADER,
    });
    const absorb = await createAbsorbRunSpec({
      repoRoot: "/repo",
      context: "Session transcript.",
      loadPrompt: TEST_PROMPT_LOADER,
    });
    const garden = await createGardenRunSpec({
      repoRoot: "/repo",
      loadPrompt: TEST_PROMPT_LOADER,
    });

    expect(build.provider).toEqual({ id: "codex", model: "gpt-5.5" });
    expect(absorb.provider).toEqual({ id: "codex", model: "gpt-5.5" });
    expect(garden.provider).toEqual({ id: "codex", model: "gpt-5.5" });
  });
});
