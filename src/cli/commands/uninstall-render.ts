import { BLUE, DIM, RST } from "../../ansi.js";
import type { SetupUninstallResult } from "../../services/setup/index.js";

type CheckedAutomation = Extract<
  SetupUninstallResult["automation"],
  { action: "checked" }
>;

export function renderUninstallStart(): string {
  return "\n";
}

export function renderAutomationKept(): string {
  return `  ${DIM}\u25cb  Scheduled automation kept${RST}\n`;
}

export function renderGuidesKept(): string {
  return `  ${DIM}\u25cb  Guides kept${RST}\n`;
}

export function renderUninstallResult(result: SetupUninstallResult): string {
  return renderAutomationResult(result.automation) +
    renderGuidesResult(result.guides);
}

export function renderUninstallComplete(): string {
  return `\n  ${BLUE}\u25c7${RST}  ${BLUE}Uninstall complete${RST}\n\n`;
}

export function renderConfirmationPrompt(
  question: string,
  defaultYes: boolean,
): string {
  const hint = defaultYes ? "[Y/n]" : "[y/N]";
  return `  ${BLUE}\u25c6${RST}  ${question} ${DIM}${hint}${RST} `;
}

function renderAutomationResult(
  result: SetupUninstallResult["automation"],
): string {
  if (result.action !== "checked") return "";

  return `  ${BLUE}\u25c7${RST}  ${formatAutomationResult(result)}\n`;
}

function renderGuidesResult(result: SetupUninstallResult["guides"]): string {
  if (result.action !== "checked") return "";

  if (!result.anyChanges) {
    return `  ${DIM}\u25cb  Guides not installed${RST}\n`;
  }

  return (
    `  ${BLUE}\u25c7${RST}  Guides removed (` +
    `${result.filesTouched.join(", ")})\n`
  );
}

function formatAutomationResult(result: CheckedAutomation): string {
  if (result.status === "not-installed") {
    return "almanac: automation not installed";
  }

  return (
    "almanac: automation removed\n" +
    result.plistPaths.map((pathValue) => `  plist: ${pathValue}\n`).join("")
  ).trim();
}
