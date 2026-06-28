import path from "node:path";

export interface UninstallTargetDirs {
  claudeDir: string;
  codexDir: string;
  cursorDir: string;
  windsurfDir: string;
  opencodeDir: string;
}

export function resolveUninstallTargetDirs(options: {
  homeDir: string;
  claudeDir?: string;
  codexDir?: string;
  cursorDir?: string;
  windsurfDir?: string;
  opencodeDir?: string;
}): UninstallTargetDirs {
  return {
    claudeDir: options.claudeDir ?? path.join(options.homeDir, ".claude"),
    codexDir: options.codexDir ?? path.join(options.homeDir, ".codex"),
    cursorDir: options.cursorDir ?? path.join(options.homeDir, ".cursor"),
    windsurfDir:
      options.windsurfDir ??
      path.join(options.homeDir, ".codeium", "windsurf"),
    opencodeDir:
      options.opencodeDir ?? path.join(options.homeDir, ".config", "opencode"),
  };
}
