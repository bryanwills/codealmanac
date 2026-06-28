export interface AnsiTheme {
  RST: string;
  BOLD: string;
  DIM: string;
  GREEN: string;
  RED: string;
  BLUE: string;
  YELLOW: string;
  WHITE_BOLD: string;
  BLUE_DIM: string;
  ACCENT_BG: string;
}

export function makeAnsiTheme(useColor: boolean): AnsiTheme {
  return {
    RST: useColor ? "\x1b[0m" : "",
    BOLD: useColor ? "\x1b[1m" : "",
    DIM: useColor ? "\x1b[2m" : "",
    GREEN: useColor ? "\x1b[38;5;35m" : "",
    RED: useColor ? "\x1b[38;5;167m" : "",
    BLUE: useColor ? "\x1b[38;5;75m" : "",
    YELLOW: useColor ? "\x1b[33m" : "",
    WHITE_BOLD: useColor ? "\x1b[1;37m" : "",
    BLUE_DIM: useColor ? "\x1b[38;5;69m" : "",
    ACCENT_BG: useColor ? "\x1b[48;5;252m\x1b[38;5;16m" : "",
  };
}
