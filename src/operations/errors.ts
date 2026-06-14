import {
  UserFacingError,
  type UserFacingErrorOptions,
  type UserFacingErrorOutcome,
} from "../errors.js";

export type OperationErrorOutcome = UserFacingErrorOutcome;

export class OperationError extends UserFacingError {
  constructor(
    message: string,
    options: UserFacingErrorOptions = {},
  ) {
    super(message, options);
  }
}

export class MissingWikiError extends OperationError {
  constructor() {
    super(
      "no Almanac wiki found in this directory or any parent",
      {
        outcome: "needs-action",
        fix: "run: almanac init",
      },
    );
  }
}
