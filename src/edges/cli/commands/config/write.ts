import {
  setConfigEntryByKey,
  unsetConfigEntryByKey,
} from "../../../../services/config/index.js";
import {
  renderConfigException,
  renderConfigSet,
  renderConfigUnset,
  type ConfigResult,
} from "./render.js";

interface ConfigCommandScope {
  cwd: string;
}

export async function runConfigSet(opts: ConfigCommandScope & {
  key: string;
  value?: string;
  project?: boolean;
}): Promise<ConfigResult> {
  try {
    return renderConfigSet(
      await setConfigEntryByKey({
        key: opts.key,
        value: opts.value,
        project: opts.project === true,
        cwd: opts.cwd,
      }),
    );
  } catch (err: unknown) {
    return renderConfigException(err);
  }
}

export async function runConfigUnset(opts: ConfigCommandScope & {
  key: string;
  project?: boolean;
}): Promise<ConfigResult> {
  return renderConfigUnset(
    await unsetConfigEntryByKey({
      key: opts.key,
      project: opts.project === true,
      cwd: opts.cwd,
    }),
  );
}
