import {
  checkSqliteAbi,
  shouldCheckSqliteAbi,
} from "../src/edges/cli/abi-guard.js";
import { renderErrorText } from "../src/edges/cli/commands/outcome.js";

// ABI guard: detect better-sqlite3 binding mismatch before commands that may
// touch the indexer. Skip setup/version/update-only paths so a fresh
// `almanac` setup or `npx codealmanac` bootstrap can install/fix itself even
// when the native binding is broken.
if (shouldCheckSqliteAbi(process.argv)) {
  const abiError = checkSqliteAbi();
  if (abiError !== null) {
    process.stderr.write(`almanac: ${abiError}\n`);
    process.exit(1);
  }
}

const { run } = await import("../src/cli.js");

run(process.argv).catch((err: unknown) => {
  process.stderr.write(renderErrorText(err));
  process.exit(1);
});
