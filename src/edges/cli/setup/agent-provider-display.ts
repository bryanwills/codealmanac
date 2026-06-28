import type { SetupProviderView } from "../../../services/setup/index.js";
import { normalizeSetupProviderFixCommand } from "../../../services/setup/index.js";
import {
  type SetupTheme,
  dim,
  whiteBold,
} from "./output.js";

type SetupProviderChoice = SetupProviderView["choices"][number];

export function formatProviderChoice(
  theme: SetupTheme,
  choice: SetupProviderChoice,
): string {
  const status = providerStatusLabel(choice);
  const detail = providerDetailLabel(choice);
  const tag = choice.recommended
    ? `  ${dim(theme, "recommended")}`
    : "";
  return `${choice.label.padEnd(8)} ${status.padEnd(15)} ${detail}${tag}`;
}

export function providerDetailLabel(choice: SetupProviderChoice): string {
  if (choice.ready) return choice.account ?? choice.detail;
  if (choice.fixCommand === null) return choice.detail;
  return normalizeSetupProviderFixCommand(choice.fixCommand) ?? choice.detail;
}

export function showUnavailableProvider(
  out: NodeJS.WritableStream,
  theme: SetupTheme,
  choice: SetupProviderChoice,
): void {
  if (choice.readiness === "missing") {
    out.write(
      `\n  ${whiteBold(theme, `${choice.label} is not installed.`)}\n` +
        `  ${providerDetailLabel(choice)}\n\n`,
    );
    return;
  }
  out.write(
    `\n  ${whiteBold(theme, `${choice.label} is not signed in.`)}\n` +
      `  Run: ${providerDetailLabel(choice)}\n\n`,
  );
}

function providerStatusLabel(choice: SetupProviderChoice): string {
  if (choice.ready) {
    return choice.detail === "ANTHROPIC_API_KEY set" ? "API key set" : "signed in";
  }
  return choice.readiness === "missing" ? "not installed" : "sign in needed";
}
