import {
  blue,
  dim,
  type SetupTheme,
} from "./output.js";
import type { SetupInputStream } from "./types.js";

export type InstallDecision = "install" | "skip";

export function confirm(
  input: SetupInputStream,
  out: NodeJS.WritableStream,
  theme: SetupTheme,
  question: string,
  defaultYes: boolean,
): Promise<InstallDecision> {
  return readLinePrompt({
    input,
    out,
    prompt: `  ${blue(theme, "◆")}  ${question} ${dim(theme, defaultYes ? "[Y/n]" : "[y/N]")} `,
    resolve: (answer) => {
      const normalized = answer.toLowerCase();
      const accepted =
        normalized.length === 0
          ? defaultYes
          : normalized === "y" || normalized === "yes";
      return accepted ? "install" : "skip";
    },
  });
}

export function promptText(
  input: SetupInputStream,
  out: NodeJS.WritableStream,
  theme: SetupTheme,
  question: string,
  defaultValue: string,
): Promise<string> {
  return readLinePrompt({
    input,
    out,
    prompt: `  ${blue(theme, "◆")}  ${question} ${dim(theme, `[${defaultValue}]`)} `,
    resolve: (answer) => answer.length === 0 ? defaultValue : answer,
  });
}

export async function waitForEnter(
  input: SetupInputStream,
  out: NodeJS.WritableStream,
  theme: SetupTheme,
  message: string,
): Promise<void> {
  await promptText(input, out, theme, message, "");
}

function readLinePrompt<T>(args: {
  input: SetupInputStream;
  out: NodeJS.WritableStream;
  prompt: string;
  resolve: (answer: string) => T;
}): Promise<T> {
  return new Promise((resolve) => {
    args.out.write(args.prompt);

    let buf = "";
    const onData = (chunk: Buffer): void => {
      buf += chunk.toString("utf8");
      const nl = buf.indexOf("\n");
      if (nl === -1) return;
      args.input.removeListener("data", onData);
      args.input.pause();
      resolve(args.resolve(buf.slice(0, nl).trim()));
    };

    args.input.resume();
    args.input.on("data", onData);
  });
}
