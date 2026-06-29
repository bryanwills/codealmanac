export const RST = "\x1b[0m";
export const BOLD = "\x1b[1m";
export const DIM = "\x1b[2m";
export const WHITE_BOLD = "\x1b[1;37m";
export const BLUE = "\x1b[38;5;75m";
export const BLUE_DIM = "\x1b[38;5;69m";
const ACCENT_BG = "\x1b[48;5;252m\x1b[38;5;16m";

const GRADIENT = [
  "\x1b[38;5;255m",
  "\x1b[38;5;253m",
  "\x1b[38;5;251m",
  "\x1b[38;5;249m",
  "\x1b[38;5;246m",
  "\x1b[38;5;243m",
];

const LOGO_LINES = [
  " \u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2557     \u2588\u2588\u2588\u2557   \u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2557   \u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2588\u2588\u2588\u2588\u2557",
  "\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2551     \u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d",
  "\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2551     \u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2554\u2588\u2588\u2557 \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2551     ",
  "\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2551\u2588\u2588\u2551     \u2588\u2588\u2551\u255a\u2588\u2588\u2554\u255d\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2551\u2588\u2588\u2551\u255a\u2588\u2588\u2557\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2551\u2588\u2588\u2551     ",
  "\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2551 \u255a\u2550\u255d \u2588\u2588\u2551\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551 \u255a\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2551  \u2588\u2588\u2551\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2557",
  "\u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d     \u255a\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u2550\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u255d",
];

export const BAR = `  ${DIM}\u2502${RST}`;

export function printBanner(
  out: NodeJS.WritableStream,
  subtitle = "a living wiki for codebases, for your agent",
): void {
  out.write("\n");
  for (let i = 0; i < LOGO_LINES.length; i++) {
    const color = GRADIENT[i] ?? GRADIENT[GRADIENT.length - 1] ?? "";
    out.write(`${color}${LOGO_LINES[i]}${RST}\n`);
  }
  out.write(`\n${WHITE_BOLD}  ${subtitle}${RST}\n`);
}

export function printBadge(out: NodeJS.WritableStream): void {
  out.write(`\n   ${ACCENT_BG} almanac ${RST}\n\n`);
}

export function stepDone(out: NodeJS.WritableStream, msg: string): void {
  out.write(`  ${BLUE}\u25c7${RST}  ${msg}\n`);
}

export function stepActive(out: NodeJS.WritableStream, msg: string): void {
  out.write(`  ${BLUE}\u25c6${RST}  ${msg}\n`);
}

export function stepSkipped(out: NodeJS.WritableStream, msg: string): void {
  out.write(`  ${DIM}\u25cb  ${msg}${RST}\n`);
}

export function renderNextStepsBox(
  out: NodeJS.WritableStream,
  lines: string[],
): void {
  const header = `  ${WHITE_BOLD}Next steps${RST}`;
  const innerW = getBoxInnerWidth(out, [header, ...lines]);
  const empty = boxRow("", innerW);

  writeLine(out, `  ${BLUE_DIM}\u256d${"─".repeat(innerW)}\u256e${RST}`);
  writeLine(out, empty);
  writeLine(out, boxRow(header, innerW));
  writeLine(out, empty);
  for (const line of lines) {
    writeLine(out, boxRow(line, innerW));
  }
  writeLine(out, empty);
  writeLine(out, `  ${BLUE_DIM}\u2570${"─".repeat(innerW)}\u256f${RST}`);
  writeLine(out, "");
}

function getBoxInnerWidth(
  out: NodeJS.WritableStream,
  contents: string[],
  minWidth = 62,
): number {
  const terminalWidth = getTerminalColumns(out);
  const available = Math.max(40, terminalWidth - 6);
  const widest = contents.reduce(
    (max, content) => Math.max(max, visibleLength(content)),
    0,
  );
  return Math.min(Math.max(minWidth, widest), available);
}

function boxRow(content: string, innerW: number): string {
  const padding = Math.max(0, innerW - visibleLength(content));
  return `  ${BLUE_DIM}\u2502${RST}${content}${" ".repeat(padding)}${BLUE_DIM}\u2502${RST}`;
}

function visibleLength(s: string): number {
  return s.replace(/\x1b\[[0-9;]*m/g, "").length;
}

function writeLine(out: NodeJS.WritableStream, line: string): void {
  out.write(`${line}\n`);
}

function getTerminalColumns(out: NodeJS.WritableStream): number {
  const stream = out as NodeJS.WriteStream;
  return stream.columns ?? process.stdout.columns ?? 80;
}

export type InstallDecision = "install" | "skip";

export function confirm(
  out: NodeJS.WritableStream,
  question: string,
  defaultYes: boolean,
): Promise<InstallDecision> {
  return new Promise((resolve) => {
    const hint = defaultYes ? "[Y/n]" : "[y/N]";
    out.write(`  ${BLUE}\u25c6${RST}  ${question} ${DIM}${hint}${RST} `);

    let buf = "";
    const onData = (chunk: Buffer): void => {
      buf += chunk.toString("utf8");
      const nl = buf.indexOf("\n");
      if (nl === -1) return;
      process.stdin.removeListener("data", onData);
      process.stdin.pause();

      const answer = buf.slice(0, nl).trim().toLowerCase();
      const accepted =
        answer.length === 0
          ? defaultYes
          : answer === "y" || answer === "yes";
      resolve(accepted ? "install" : "skip");
    };

    process.stdin.resume();
    process.stdin.on("data", onData);
  });
}

export function promptText(
  out: NodeJS.WritableStream,
  question: string,
  defaultValue: string,
): Promise<string> {
  return new Promise((resolve) => {
    out.write(
      `  ${BLUE}\u25c6${RST}  ${question} ${DIM}[${defaultValue}]${RST} `,
    );

    let buf = "";
    const onData = (chunk: Buffer): void => {
      buf += chunk.toString("utf8");
      const nl = buf.indexOf("\n");
      if (nl === -1) return;
      process.stdin.removeListener("data", onData);
      process.stdin.pause();

      const answer = buf.slice(0, nl).trim();
      resolve(answer.length === 0 ? defaultValue : answer);
    };

    process.stdin.resume();
    process.stdin.on("data", onData);
  });
}

export async function waitForEnter(
  out: NodeJS.WritableStream,
  message: string,
): Promise<void> {
  await promptText(out, message, "");
}

export interface SelectChoice<T> {
  value: T;
  line: string;
  aliases?: string[];
}

export async function selectChoice<T>(args: {
  out: NodeJS.WritableStream;
  title: string;
  help?: string;
  choices: SelectChoice<T>[];
  defaultIndex: number;
}): Promise<T> {
  const selected = clampIndex(args.defaultIndex, args.choices.length);
  if (canUseRawSelect()) {
    return await selectChoiceRaw({ ...args, defaultIndex: selected });
  }
  renderSelect(args.out, {
    title: args.title,
    help: args.help,
    choices: args.choices,
    selected,
    raw: false,
  });
  const answer = await promptText(args.out, "Select", String(selected + 1));
  const index = Number.parseInt(answer, 10);
  if (
    Number.isInteger(index) &&
    index >= 1 &&
    index <= args.choices.length
  ) {
    return args.choices[index - 1]!.value;
  }
  const normalized = answer.trim().toLowerCase();
  const matched = args.choices.find((choice) =>
    choice.aliases?.some((alias) => alias.toLowerCase() === normalized)
  );
  return (matched ?? args.choices[selected])!.value;
}

async function selectChoiceRaw<T>(args: {
  out: NodeJS.WritableStream;
  title: string;
  help?: string;
  choices: SelectChoice<T>[];
  defaultIndex: number;
}): Promise<T> {
  return new Promise((resolve, reject) => {
    let selected = args.defaultIndex;
    let renderedLines = 0;
    const input = process.stdin as NodeJS.ReadStream & {
      setRawMode?: (mode: boolean) => void;
    };
    const render = (): void => {
      if (renderedLines > 0) {
        args.out.write(`\x1b[${renderedLines}A\x1b[0J`);
      }
      renderedLines = renderSelect(args.out, {
        title: args.title,
        help: args.help,
        choices: args.choices,
        selected,
        raw: true,
      });
    };
    const cleanup = (): void => {
      input.removeListener("data", onData);
      input.setRawMode?.(false);
      input.pause();
    };
    const onData = (chunk: Buffer): void => {
      const key = chunk.toString("utf8");
      if (key === "\u0003") {
        cleanup();
        args.out.write("\n");
        reject(new SetupInterruptedError());
        return;
      }
      if (key === "\r" || key === "\n") {
        cleanup();
        args.out.write("\n");
        resolve(args.choices[selected]!.value);
        return;
      }
      if (key === "\u001b[A") {
        selected = selected === 0 ? args.choices.length - 1 : selected - 1;
        render();
      } else if (key === "\u001b[B") {
        selected = selected === args.choices.length - 1 ? 0 : selected + 1;
        render();
      }
    };
    input.setRawMode?.(true);
    input.resume();
    input.on("data", onData);
    render();
  });
}

function renderSelect<T>(
  out: NodeJS.WritableStream,
  args: {
    title: string;
    help?: string;
    choices: SelectChoice<T>[];
    selected: number;
    raw: boolean;
  },
): number {
  let lines = 0;
  out.write(`  ${WHITE_BOLD}${args.title}${RST}\n`);
  lines++;
  if (args.help !== undefined) {
    out.write(`  ${DIM}${args.help}${RST}\n`);
    lines++;
  }
  out.write("\n");
  lines++;
  args.choices.forEach((choice, index) => {
    const pointer = index === args.selected ? `${BLUE}\u203a${RST}` : " ";
    out.write(`  ${pointer} ${choice.line}\n`);
    lines++;
  });
  const hint = args.raw
    ? `Use \u2191/\u2193 to move, Enter to select`
    : `Type a number or name, then press Enter`;
  out.write(`\n  ${DIM}${hint}${RST}\n`);
  lines += 2;
  return lines;
}

export class SetupInterruptedError extends Error {
  constructor() {
    super("setup interrupted");
  }
}

export function isSetupInterrupted(err: unknown): boolean {
  return err instanceof SetupInterruptedError;
}

function canUseRawSelect(): boolean {
  const input = process.stdin as NodeJS.ReadStream & {
    setRawMode?: (mode: boolean) => void;
  };
  return process.stdin.isTTY === true && typeof input.setRawMode === "function";
}

function clampIndex(index: number, length: number): number {
  if (length <= 0) return 0;
  if (index < 0) return 0;
  if (index >= length) return length - 1;
  return index;
}
