import {
  blue,
  bold,
  controlLabel,
  dim,
  type SetupTheme,
  whiteBold,
  writeSetupDivider,
} from "./output.js";
import {
  SetupInterruptedError,
} from "./input.js";
import type { SetupInputStream } from "./types.js";

export interface MultiSelectChoice<T> {
  value: T;
  label: string;
}

export function canUseRawSelect(input: SetupInputStream): boolean {
  return input.isTTY === true && typeof input.setRawMode === "function";
}

export function selectManyRaw<T>(args: {
  input: SetupInputStream;
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  title: string;
  choices: readonly MultiSelectChoice<T>[];
  selected: Set<T>;
}): Promise<T[]> {
  return new Promise((resolve, reject) => {
    const selected = new Set(args.selected);
    let cursor = 0;
    let renderedLines = 0;
    const render = (): void => {
      if (renderedLines > 0) {
        args.out.write(`\x1b[${renderedLines}A\x1b[0J`);
      }
      renderedLines = renderMultiSelect(args.out, args.theme, {
        title: args.title,
        choices: args.choices,
        selected,
        cursor,
      });
    };
    const cleanup = (): void => {
      args.input.removeListener("data", onData);
      args.input.setRawMode?.(false);
      args.input.pause();
    };
    const onData = (chunk: Buffer): void => {
      const key = chunk.toString("utf8");
      if (key === "\u0003" || key === "q") {
        cleanup();
        args.out.write("\n");
        reject(new SetupInterruptedError());
        return;
      }
      if (key === "\u001b[A" || key === "k") {
        cursor = cursor === 0 ? args.choices.length - 1 : cursor - 1;
        render();
        return;
      }
      if (key === "\u001b[B" || key === "j") {
        cursor = cursor === args.choices.length - 1 ? 0 : cursor + 1;
        render();
        return;
      }
      if (key === " ") {
        const value = args.choices[cursor]!.value;
        if (selected.has(value)) selected.delete(value);
        else selected.add(value);
        render();
        return;
      }
      if (key === "a") {
        const allSelected = selected.size === args.choices.length;
        selected.clear();
        if (!allSelected) {
          for (const choice of args.choices) selected.add(choice.value);
        }
        render();
        return;
      }
      if (key === "\r" || key === "\n") {
        cleanup();
        args.out.write("\n");
        resolve(orderedSelectedValues(args.choices, selected));
      }
    };
    args.input.setRawMode?.(true);
    args.input.resume();
    args.input.on("data", onData);
    render();
  });
}

function renderMultiSelect<T>(
  out: NodeJS.WritableStream,
  theme: SetupTheme,
  args: {
    title: string;
    choices: readonly MultiSelectChoice<T>[];
    selected: Set<T>;
    cursor: number;
  },
): number {
  let lines = 0;
  out.write(`  ${blue(theme, "\u25c6")}  ${whiteBold(theme, args.title)}\n`);
  lines++;
  writeSetupDivider(out, theme);
  lines++;

  args.choices.forEach((choice, index) => {
    const arrow = index === args.cursor ? blue(theme, "\u276f") : " ";
    const check = args.selected.has(choice.value)
      ? blue(theme, "\u2713")
      : " ";
    const label = index === args.cursor ? bold(theme, choice.label) : choice.label;
    out.write(`  ${dim(theme, "\u2502")}   ${arrow} [${check}] ${label}\n`);
    lines++;
  });

  writeSetupDivider(out, theme);
  lines++;
  out.write(`  ${dim(theme, "\u2502")}   ${rawModeHint(theme)}\n`);
  lines++;
  return lines;
}

function rawModeHint(theme: SetupTheme): string {
  return [
    `${controlLabel(theme, "[space]")} toggle`,
    `${controlLabel(theme, "[↑↓]")} move`,
    `${controlLabel(theme, "[a]")} all`,
    `${controlLabel(theme, "[enter]")} confirm`,
    `${dim(theme, "[q] quit")}`,
  ].join("  ");
}

function orderedSelectedValues<T>(
  choices: readonly MultiSelectChoice<T>[],
  selected: Set<T>,
): T[] {
  return choices
    .map((choice) => choice.value)
    .filter((value) => selected.has(value));
}
