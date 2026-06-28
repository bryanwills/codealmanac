import {
  listConfigEntries,
  readConfigEntryByKey,
} from "../../../../services/config/index.js";
import {
  renderConfigGet,
  renderConfigList,
  type ConfigResult,
} from "./render.js";

export async function runConfigList(opts: {
  cwd: string;
  json?: boolean;
  showOrigin?: boolean;
}): Promise<ConfigResult> {
  return renderConfigList(await listConfigEntries({ cwd: opts.cwd }), opts);
}

export async function runConfigGet(opts: {
  cwd: string;
  key: string;
  json?: boolean;
  showOrigin?: boolean;
}): Promise<ConfigResult> {
  return renderConfigGet(
    await readConfigEntryByKey({ key: opts.key, cwd: opts.cwd }),
    opts,
  );
}
