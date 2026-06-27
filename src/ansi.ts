import { makeAnsiTheme } from "./ansi-theme.js";
export { makeAnsiTheme, type AnsiTheme } from "./ansi-theme.js";

/**
 * Shared ANSI escape-code constants. TTY-aware: when stdout is not a
 * terminal or `NO_COLOR` is set, every constant resolves to the empty
 * string so formatted output degrades to plain text without per-call
 * checks at every use site.
 *
 * See https://no-color.org/ for the `NO_COLOR` convention.
 */

const defaultTheme = makeAnsiTheme(
  (process.stdout.isTTY ?? false) && !("NO_COLOR" in process.env),
);

export const {
  RST,
  BOLD,
  DIM,
  GREEN,
  RED,
  BLUE,
  YELLOW,
  WHITE_BOLD,
  BLUE_DIM,
  ACCENT_BG,
} = defaultTheme;
