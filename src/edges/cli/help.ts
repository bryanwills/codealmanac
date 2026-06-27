import { Command, type Help } from "commander";

import { makeAnsiTheme, type AnsiTheme } from "../../ansi-theme.js";
import { shouldUseStdoutColor } from "./helpers.js";

const HELP_GROUPS: Array<{ title: string; commands: string[] }> = [
  {
    title: "Query",
    commands: ["search", "show", "health", "list"],
  },
  {
    title: "Edit",
    commands: ["tag", "untag", "topics"],
  },
  {
    title: "Wiki lifecycle",
    commands: [
      "init",
      "absorb",
      "sync",
      "ingest",
      "garden",
      "jobs",
      "automation",
      "reindex",
    ],
  },
  {
    title: "Setup",
    commands: ["agents", "config", "setup", "uninstall", "doctor", "update"],
  },
  {
    title: "Deprecated",
    commands: ["set", "ps"],
  },
];

/**
 * Install a custom `formatHelp` that replaces commander's flat
 * "Commands:" section with grouped headings. Keeps usage + options +
 * per-command short descriptions; only the commands section changes.
 */
export function configureGroupedHelp(program: Command): void {
  program.configureHelp({
    formatHelp(cmd, helper): string {
      const theme = makeAnsiTheme(shouldUseStdoutColor());
      if (cmd.parent !== null) {
        return renderDefault(cmd, helper, theme);
      }

      const termWidth = helper.padWidth(cmd, helper);
      const helpWidth =
        helper.helpWidth ?? process.stdout.columns ?? 80;
      const itemSepWidth = 2;

      const out: string[] = [];
      out.push(`${theme.BOLD}Usage:${theme.RST} ${helper.commandUsage(cmd)}\n`);

      const description = helper.commandDescription(cmd);
      if (description.length > 0) {
        out.push(
          helper.wrap(description, helpWidth, 0) + "\n",
        );
      }

      const optionList = helper
        .visibleOptions(cmd)
        .map((o) => {
          return formatHelpRow({
            term: helper.optionTerm(o),
            description: helper.optionDescription(o),
            termWidth,
            itemSepWidth,
            theme,
          });
        });
      if (optionList.length > 0) {
        out.push(`${theme.BOLD}Options:${theme.RST}`);
        for (const l of optionList) out.push(`  ${l}`);
        out.push("");
      }

      const visible = helper.visibleCommands(cmd);
      const byName = new Map<string, (typeof visible)[number]>();
      for (const c of visible) byName.set(c.name(), c);

      for (const group of HELP_GROUPS) {
        const members = group.commands
          .map((n) => byName.get(n))
          .filter((c): c is (typeof visible)[number] => c !== undefined);
        if (members.length === 0) continue;
        out.push(`${theme.BOLD}${group.title}:${theme.RST}`);
        for (const c of members) {
          const term = helper.subcommandTerm(c);
          out.push(`  ${formatHelpRow({
            term,
            description: helper.subcommandDescription(c),
            termWidth,
            itemSepWidth,
            theme,
          })}`);
          byName.delete(c.name());
        }
        out.push("");
      }

      byName.delete("help");
      if (byName.size > 0) {
        out.push(`${theme.BOLD}Other:${theme.RST}`);
        for (const c of byName.values()) {
          const term = helper.subcommandTerm(c);
          out.push(`  ${formatHelpRow({
            term,
            description: helper.subcommandDescription(c),
            termWidth,
            itemSepWidth,
            theme,
          })}`);
        }
        out.push("");
      }

      return out.join("\n");
    },
  });
}

function renderDefault(cmd: Command, helper: Help, theme: AnsiTheme): string {
  const termWidth = helper.padWidth(cmd, helper);
  const helpWidth = helper.helpWidth ?? process.stdout.columns ?? 80;
  const itemSepWidth = 2;

  const lines: string[] = [
    `${theme.BOLD}Usage:${theme.RST} ${helper.commandUsage(cmd)}\n`,
  ];
  const description = helper.commandDescription(cmd);
  if (description.length > 0) {
    lines.push(helper.wrap(description, helpWidth, 0) + "\n");
  }

  const args = helper.visibleArguments(cmd).map((a) => {
    return formatHelpRow({
      term: helper.argumentTerm(a),
      description: helper.argumentDescription(a),
      termWidth,
      itemSepWidth,
      theme,
    });
  });
  if (args.length > 0) {
    lines.push(`${theme.BOLD}Arguments:${theme.RST}`);
    for (const a of args) lines.push(`  ${a}`);
    lines.push("");
  }

  const opts = helper.visibleOptions(cmd).map((o) => {
    return formatHelpRow({
      term: helper.optionTerm(o),
      description: helper.optionDescription(o),
      termWidth,
      itemSepWidth,
      theme,
    });
  });
  if (opts.length > 0) {
    lines.push(`${theme.BOLD}Options:${theme.RST}`);
    for (const o of opts) lines.push(`  ${o}`);
    lines.push("");
  }

  const subs = helper.visibleCommands(cmd).map((c) => {
    return formatHelpRow({
      term: helper.subcommandTerm(c),
      description: helper.subcommandDescription(c),
      termWidth,
      itemSepWidth,
      theme,
    });
  });
  if (subs.length > 0) {
    lines.push(`${theme.BOLD}Commands:${theme.RST}`);
    for (const s of subs) lines.push(`  ${s}`);
    lines.push("");
  }

  return lines.join("\n");
}

function formatHelpRow(options: {
  term: string;
  description: string;
  termWidth: number;
  itemSepWidth: number;
  theme: AnsiTheme;
}): string {
  const { term, description, termWidth, itemSepWidth, theme } = options;
  const padding = Math.max(0, termWidth - term.length + itemSepWidth);
  return (
    `${theme.BLUE}${term}${theme.RST}` +
    `${" ".repeat(padding)}` +
    `${theme.DIM}${description}${theme.RST}`
  );
}
