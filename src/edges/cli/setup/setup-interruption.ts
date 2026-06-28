export class SetupInterruptedError extends Error {
  constructor() {
    super("setup interrupted");
  }
}

export function isSetupInterrupted(err: unknown): boolean {
  return err instanceof SetupInterruptedError;
}
