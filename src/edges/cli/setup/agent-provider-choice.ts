import type {
  SetupAgentProviderId,
  SetupProviderFixCommandRunner,
  SetupProviderView,
  SetupSpawnCliFn,
} from "../../../services/setup/index.js";
import type { AgentReadinessRuntime } from "../../../shared/agent-readiness.js";
import {
  normalizeSetupProviderFixCommand,
  refreshSetupAgentChoiceView,
  runnableSetupProviderFixCommand,
  runSetupProviderFixCommand,
} from "../../../services/setup/index.js";
import {
  confirm,
  waitForEnter,
} from "./line-prompt.js";
import {
  selectChoice,
} from "./select-choice.js";
import type { SetupTheme } from "./output.js";
import {
  stepActive,
} from "./output.js";
import {
  formatProviderChoice,
  showUnavailableProvider,
} from "./agent-provider-display.js";
import type { SetupInputStream } from "./types.js";

type SetupProviderChoice = SetupProviderView["choices"][number];

interface ProviderChoiceContext {
  input: SetupInputStream;
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  readinessRuntime: AgentReadinessRuntime;
  spawnCli?: SetupSpawnCliFn;
  runProviderFixCommand: SetupProviderFixCommandRunner;
  environment: NodeJS.ProcessEnv;
}

export async function chooseInteractiveSetupProvider(
  args: ProviderChoiceContext & { view: SetupProviderView },
): Promise<{ selected: SetupAgentProviderId; view: SetupProviderView }> {
  let view = args.view;
  while (true) {
    const choice = await selectChoice({
      input: args.input,
      out: args.out,
      theme: args.theme,
      title: "Choose your agent",
      help: "Choose the AI agent Almanac should use.",
      choices: view.choices.map((choice) => ({
        value: choice,
        line: formatProviderChoice(args.theme, choice),
        aliases: [choice.id, choice.label.toLowerCase()],
      })),
      defaultIndex: Math.max(
        0,
        view.choices.findIndex((choice) =>
          choice.id === view.recommendedProvider
        ),
      ),
    });
    if (choice.ready) {
      return { selected: choice.id, view };
    }
    const refreshed = await tryRunProviderLogin({
      ...args,
      view,
      choice,
    });
    if (refreshed !== null) {
      view = refreshed;
      const refreshedChoice = view.choices.find((next) => next.id === choice.id);
      if (refreshedChoice?.ready === true) {
        return { selected: refreshedChoice.id, view };
      }
      continue;
    }
    showUnavailableProvider(args.out, args.theme, choice);
    await waitForEnter(
      args.input,
      args.out,
      args.theme,
      "Press Enter to choose a different agent.",
    );
  }
}

export async function promptForSelectedProviderFix(
  args: ProviderChoiceContext & {
    provider: SetupAgentProviderId;
    selectedChoice: SetupProviderChoice;
  },
): Promise<{
  view: SetupProviderView | null;
  selectedChoice: SetupProviderChoice;
}> {
  if (args.selectedChoice.ready) {
    return { view: null, selectedChoice: args.selectedChoice };
  }
  const runnableFixCommand = runnableSetupProviderFixCommand(
    args.selectedChoice.fixCommand,
  );
  if (runnableFixCommand === null) {
    return { view: null, selectedChoice: args.selectedChoice };
  }
  const runLogin = await confirm(
    args.input,
    args.out,
    args.theme,
    `${args.selectedChoice.label} is not ready. Run '${runnableFixCommand}' now?`,
    true,
  );
  if (runLogin !== "install") {
    return { view: null, selectedChoice: args.selectedChoice };
  }
  const login = await runSetupProviderFixCommand(
    runnableFixCommand,
    args.runProviderFixCommand,
  );
  if (!login.ok) {
    stepActive(
      args.out,
      args.theme,
      `${args.selectedChoice.label} login failed: ${login.error}`,
    );
    return { view: null, selectedChoice: args.selectedChoice };
  }
  const view = await refreshSetupAgentChoiceView({
    readinessRuntime: args.readinessRuntime,
    spawnCli: args.spawnCli,
    environment: args.environment,
  });
  return {
    view,
    selectedChoice: view.choices.find((choice) => choice.id === args.provider) ??
      args.selectedChoice,
  };
}

async function tryRunProviderLogin(
  args: ProviderChoiceContext & {
    view: SetupProviderView;
    choice: SetupProviderChoice;
  },
): Promise<SetupProviderView | null> {
  const command = normalizeSetupProviderFixCommand(args.choice.fixCommand);
  if (args.choice.readiness !== "not-authenticated" || command === null) {
    return null;
  }
  const runLogin = await confirm(
    args.input,
    args.out,
    args.theme,
    `${args.choice.label} sign-in is needed. Run '${command}' now?`,
    true,
  );
  if (runLogin !== "install") {
    return args.view;
  }
  const login = await runSetupProviderFixCommand(
    command,
    args.runProviderFixCommand,
  );
  if (!login.ok) {
    stepActive(
      args.out,
      args.theme,
      `${args.choice.label} login failed: ${login.error}`,
    );
  }
  return refreshSetupAgentChoiceView({
    readinessRuntime: args.readinessRuntime,
    spawnCli: args.spawnCli,
    environment: args.environment,
  });
}
