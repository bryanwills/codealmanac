import type {
  SetupAgentProviderId,
  SetupProviderView,
  SetupSpawnCliFn,
} from "../../../services/setup/index.js";
import { runInheritedShellCommand } from "../../../platform/shell.js";
import {
  readSetupAgentChoiceState,
  refreshSetupAgentChoiceView,
  resolveSetupAgentSelection,
  saveSetupAgentChoice,
} from "../../../services/setup/index.js";
import { chooseProviderModel } from "./agent-model-choice.js";
import {
  confirm,
  selectChoice,
  waitForEnter,
} from "./input.js";
import {
  DIM,
  RST,
  WHITE_BOLD,
  stepActive,
  stepDone,
} from "./output.js";

export type AgentChoice =
  | { ok: true; provider: SetupAgentProviderId; model: string | null }
  | { ok: false; error: string };

export async function chooseDefaultAgent(args: {
  out: NodeJS.WritableStream;
  interactive: boolean;
  requested?: string;
  requestedModel?: string;
  spawnCli?: SetupSpawnCliFn;
}): Promise<AgentChoice> {
  const state = await readSetupAgentChoiceState({
    requested: args.requested,
    includeView: args.interactive || args.requested !== undefined,
    spawnCli: args.spawnCli,
  });
  let view = state.view;
  let selected = state.selected;
  if (args.interactive && args.requested === undefined && view !== null) {
    while (true) {
      const choice = await selectChoice({
        out: args.out,
        title: "Choose your agent",
        help: "Choose the AI agent Almanac should use.",
        choices: view.choices.map((choice) => ({
          value: choice,
          line: formatProviderChoice(choice),
          aliases: [choice.id, choice.label.toLowerCase()],
        })),
        defaultIndex: Math.max(
          0,
          view.choices.findIndex((choice) =>
            choice.id === view?.recommendedProvider
          ),
        ),
      });
      if (choice.ready) {
        selected = choice.id;
        break;
      }
      if (choice.readiness === "not-authenticated" && choice.fixCommand !== null) {
        const command = choice.fixCommand.startsWith("run: ")
          ? choice.fixCommand.slice("run: ".length)
          : choice.fixCommand;
        const runLogin = await confirm(
          args.out,
          `${choice.label} sign-in is needed. Run '${command}' now?`,
          true,
        );
        if (runLogin === "install") {
          const login = await runInheritedShellCommand(command);
          if (!login.ok) {
            stepActive(args.out, `${choice.label} login failed: ${login.error}`);
          }
          view = await refreshSetupAgentChoiceView({
            spawnCli: args.spawnCli,
          });
          const refreshed = view.choices.find((next) => next.id === choice.id);
          if (refreshed?.ready === true) {
            selected = refreshed.id;
            break;
          }
        }
        continue;
      }
      showUnavailableProvider(args.out, choice);
      await waitForEnter(args.out, "Press Enter to choose a different agent.");
    }
  }
  const selection = resolveSetupAgentSelection(selected);
  if (!selection.ok) return selection;
  const provider = selection.provider;
  let selectedChoice = view?.choices.find((choice) => choice.id === provider);
  if (
    args.interactive &&
    selectedChoice !== undefined &&
    !selectedChoice.ready &&
    selectedChoice.fixCommand?.startsWith("run: ") === true
  ) {
    const command = selectedChoice.fixCommand.slice("run: ".length);
    const runLogin = await confirm(
      args.out,
      `${selectedChoice.label} is not ready. Run '${command}' now?`,
      true,
    );
    if (runLogin === "install") {
      const login = await runInheritedShellCommand(command);
      if (login.ok) {
        view = await refreshSetupAgentChoiceView({
          spawnCli: args.spawnCli,
        });
        selectedChoice = view.choices.find((choice) => choice.id === provider);
      } else {
        stepActive(args.out, `${selectedChoice.label} login failed: ${login.error}`);
      }
    }
  }
  if (selectedChoice !== undefined && !selectedChoice.ready) {
    return {
      ok: false,
      error: `${selectedChoice.label} is not ready: ${
        selectedChoice.fixCommand ?? selectedChoice.detail
      }`,
    };
  }
  const requestedModel = args.requestedModel ?? selection.parsedModel;
  const model = requestedModel ?? await chooseProviderModel({
    out: args.out,
    interactive: args.interactive,
    provider,
    choice: selectedChoice,
    configuredModel: state.configuredModels[provider] ?? null,
  });
  await saveSetupAgentChoice({ provider, model });
  if ((!args.interactive || args.requested !== undefined) && selectedChoice !== undefined) {
    const detail = selectedChoice?.ready === true
      ? "ready"
      : selectedChoice?.fixCommand ?? selectedChoice?.detail ?? "status unknown";
    stepDone(args.out, `Agent readiness: ${detail}`);
  }
  return { ok: true, provider, model };
}

function formatProviderChoice(
  choice: SetupProviderView["choices"][number],
): string {
  const status = providerStatusLabel(choice);
  const detail = providerDetailLabel(choice);
  const tag = choice.recommended ? `  ${DIM}recommended${RST}` : "";
  return `${choice.label.padEnd(8)} ${status.padEnd(15)} ${detail}${tag}`;
}

function providerStatusLabel(
  choice: SetupProviderView["choices"][number],
): string {
  if (choice.ready) {
    return choice.detail === "ANTHROPIC_API_KEY set" ? "API key set" : "signed in";
  }
  return choice.readiness === "missing" ? "not installed" : "sign in needed";
}

function providerDetailLabel(
  choice: SetupProviderView["choices"][number],
): string {
  if (choice.ready) return choice.account ?? choice.detail;
  if (choice.fixCommand === null) return choice.detail;
  return choice.fixCommand.startsWith("run: ")
    ? choice.fixCommand.slice("run: ".length)
    : choice.fixCommand;
}

function showUnavailableProvider(
  out: NodeJS.WritableStream,
  choice: SetupProviderView["choices"][number],
): void {
  if (choice.readiness === "missing") {
    out.write(
      `\n  ${WHITE_BOLD}${choice.label} is not installed.${RST}\n` +
        `  ${providerDetailLabel(choice)}\n\n`,
    );
    return;
  }
  out.write(
    `\n  ${WHITE_BOLD}${choice.label} is not signed in.${RST}\n` +
      `  Run: ${providerDetailLabel(choice)}\n\n`,
  );
}
