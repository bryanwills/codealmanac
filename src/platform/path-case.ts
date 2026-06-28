export function pathsEqualOnCurrentPlatform(a: string, b: string): boolean {
  return isCaseInsensitivePathPlatform(process.platform)
    ? a.toLowerCase() === b.toLowerCase()
    : a === b;
}

export function isCaseInsensitivePathPlatform(
  platform: NodeJS.Platform,
): boolean {
  return platform === "darwin" || platform === "win32";
}
