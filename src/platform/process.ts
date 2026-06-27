export function isLocalPidAlive(pid: number): boolean {
  if (pid <= 0) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

export function signalLocalPid(pid: number, signal: NodeJS.Signals): void {
  process.kill(pid, signal);
}
