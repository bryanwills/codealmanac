import { PassThrough } from "node:stream";

import { describe, expect, it } from "vitest";

import {
  buildSetupPlan,
  SETUP_DEFAULTS,
} from "../src/cli/commands/setup/setup-plan.js";
import { DEFAULT_INSTRUCTION_TARGETS } from "../src/agent/install-targets.js";

function setupOutput(): {
  out: PassThrough;
  stdout: () => string;
} {
  const out = new PassThrough();
  const chunks: Buffer[] = [];
  out.on("data", (chunk: Buffer) => chunks.push(chunk));
  return {
    out,
    stdout: () => Buffer.concat(chunks).toString("utf8"),
  };
}

describe("setup plan", () => {
  it("uses launch defaults in non-interactive setup", async () => {
    const { out } = setupOutput();

    await expect(buildSetupPlan({
      out,
      interactive: false,
      options: {},
    })).resolves.toEqual({
      instructionTargets: [...DEFAULT_INSTRUCTION_TARGETS],
      cliAutoUpdate: SETUP_DEFAULTS.cliAutoUpdate,
      cloudCapture: SETUP_DEFAULTS.cloudCapture,
      selfManagedAutomation: SETUP_DEFAULTS.selfManagedAutomation,
      autoCommit: SETUP_DEFAULTS.autoCommit,
    });
  });

  it("skip flags disable automation and instructions gates", async () => {
    const { out } = setupOutput();

    await expect(buildSetupPlan({
      out,
      interactive: false,
      options: {
        skipAutomation: true,
        skipGuides: true,
      },
    })).resolves.toMatchObject({
      instructionTargets: [],
      cliAutoUpdate: false,
      cloudCapture: false,
      selfManagedAutomation: false,
      autoCommit: false,
    });
  });

  it("explicit setup flags enable their gates", async () => {
    const { out } = setupOutput();

    await expect(buildSetupPlan({
      out,
      interactive: false,
      options: {
        automationEvery: "2h",
        autoUpdate: true,
        autoCommit: true,
        cloudCapture: true,
      },
    })).resolves.toMatchObject({
      instructionTargets: [...DEFAULT_INSTRUCTION_TARGETS],
      cloudCapture: true,
      selfManagedAutomation: true,
      cliAutoUpdate: true,
      autoCommit: true,
    });
  });

  it("explicit auto-commit opt-out keeps the gate false", async () => {
    const { out } = setupOutput();

    await expect(buildSetupPlan({
      out,
      interactive: false,
      options: {
        autoCommit: false,
      },
    })).resolves.toMatchObject({
      autoCommit: false,
    });
  });

  it("interactive answers override shown gate defaults", async () => {
    const { out, stdout } = setupOutput();
    let answeredTargets = false;
    let answeredUpdate = false;
    let answeredAutomation = false;
    out.on("data", () => {
      const text = stdout();
      if (!answeredTargets && text.includes("Select targets")) {
        answeredTargets = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("\n")));
      }
      if (!answeredUpdate && text.includes("Keep the Almanac CLI updated automatically?")) {
        answeredUpdate = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("n\n")));
      }
      if (!answeredAutomation && text.includes("Handle Almanac automations on the cloud?")) {
        answeredAutomation = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("\n")));
      }
    });

    await expect(buildSetupPlan({
      out,
      interactive: true,
      options: {},
    })).resolves.toMatchObject({
      instructionTargets: [...DEFAULT_INSTRUCTION_TARGETS],
      cliAutoUpdate: false,
      cloudCapture: true,
      selfManagedAutomation: false,
      autoCommit: false,
    });
    expect(answeredTargets).toBe(true);
    expect(answeredUpdate).toBe(true);
    expect(answeredAutomation).toBe(true);
    expect(stdout()).not.toContain("Send Claude/Codex turns to Almanac Cloud?");
  });

  it("interactive target selection can intentionally choose no targets", async () => {
    const { out, stdout } = setupOutput();
    let answeredTargets = false;
    let answeredUpdate = false;
    let answeredAutomation = false;
    out.on("data", () => {
      const text = stdout();
      if (!answeredTargets && text.includes("Select targets")) {
        answeredTargets = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("none\n")));
      }
      if (!answeredUpdate && text.includes("Keep the Almanac CLI updated automatically?")) {
        answeredUpdate = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("\n")));
      }
      if (!answeredAutomation && text.includes("Handle Almanac automations on the cloud?")) {
        answeredAutomation = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("\n")));
      }
    });

    await expect(buildSetupPlan({
      out,
      interactive: true,
      options: {},
    })).resolves.toMatchObject({
      instructionTargets: [],
      cliAutoUpdate: true,
      cloudCapture: true,
      selfManagedAutomation: false,
      autoCommit: false,
    });
    expect(answeredTargets).toBe(true);
    expect(answeredAutomation).toBe(true);
    expect(stdout()).not.toContain("Send Claude/Codex turns to Almanac Cloud?");
  });

  it("interactive cloud automation opt-out enters self-managed setup", async () => {
    const { out, stdout } = setupOutput();
    let answeredTargets = false;
    let answeredUpdate = false;
    let answeredAutomation = false;
    let answeredAutoCommit = false;
    out.on("data", () => {
      const text = stdout();
      if (!answeredTargets && text.includes("Select targets")) {
        answeredTargets = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("\n")));
      }
      if (!answeredUpdate && text.includes("Keep the Almanac CLI updated automatically?")) {
        answeredUpdate = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("\n")));
      }
      if (!answeredAutomation && text.includes("Handle Almanac automations on the cloud?")) {
        answeredAutomation = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("n\n")));
      }
      if (!answeredAutoCommit && text.includes("Commit Almanac wiki updates automatically?")) {
        answeredAutoCommit = true;
        queueMicrotask(() => process.stdin.emit("data", Buffer.from("\n")));
      }
    });

    await expect(buildSetupPlan({
      out,
      interactive: true,
      options: {},
    })).resolves.toMatchObject({
      cloudCapture: false,
      selfManagedAutomation: true,
      autoCommit: true,
    });
    expect(answeredTargets).toBe(true);
    expect(answeredUpdate).toBe(true);
    expect(answeredAutomation).toBe(true);
    expect(answeredAutoCommit).toBe(true);
    expect(stdout()).toContain("Commit Almanac wiki updates automatically? \u001b[2m[Y/n]\u001b[0m");
  });
});
