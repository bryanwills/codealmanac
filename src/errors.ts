export type UserFacingErrorOutcome = "error" | "needs-action";

export type UserFacingErrorOptions =
  | {
      outcome?: "error";
      fix?: string;
      data?: Record<string, unknown>;
    }
  | {
      outcome: "needs-action";
      fix: string;
      data?: Record<string, unknown>;
    };

export class UserFacingError extends Error {
  readonly outcome: UserFacingErrorOutcome;
  readonly fix?: string;
  readonly data?: Record<string, unknown>;

  constructor(message: string, options: UserFacingErrorOptions = {}) {
    super(message);
    this.name = new.target.name;
    this.outcome = options.outcome ?? "error";
    this.fix = options.fix;
    this.data = options.data;
  }
}
