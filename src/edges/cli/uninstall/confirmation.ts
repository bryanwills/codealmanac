import type { UninstallRenderOptions } from "../uninstall-render.js";
import { renderConfirmationPrompt } from "../uninstall-render.js";

export async function chooseUninstallRemoval(args: {
  keep: boolean | undefined;
  interactive: boolean;
  input: NodeJS.ReadableStream;
  out: NodeJS.WritableStream;
  question: string;
  renderOptions: UninstallRenderOptions;
}): Promise<boolean> {
  if (args.keep === true) return false;
  if (!args.interactive) return true;
  return confirmUninstallRemoval({
    input: args.input,
    out: args.out,
    question: args.question,
    defaultYes: true,
    renderOptions: args.renderOptions,
  });
}

function confirmUninstallRemoval(args: {
  input: NodeJS.ReadableStream;
  out: NodeJS.WritableStream;
  question: string;
  defaultYes: boolean;
  renderOptions: UninstallRenderOptions;
}): Promise<boolean> {
  return new Promise((resolve) => {
    args.out.write(
      renderConfirmationPrompt(
        args.question,
        args.defaultYes,
        args.renderOptions,
      ),
    );

    let buf = "";
    const onData = (chunk: Buffer): void => {
      buf += chunk.toString("utf8");
      const nl = buf.indexOf("\n");
      if (nl === -1) return;
      args.input.removeListener("data", onData);
      args.input.pause();

      const answer = buf.slice(0, nl).trim().toLowerCase();
      const accepted =
        answer.length === 0
          ? args.defaultYes
          : answer === "y" || answer === "yes";
      resolve(accepted);
    };

    args.input.resume();
    args.input.on("data", onData);
  });
}
