export interface UpdateLatestVersionRequest {
  timeoutMs?: number;
}

export type UpdateLatestVersionResult =
  | { ok: true; latest: string }
  | { ok: false };

export type UpdateLatestVersionFn = (
  request?: UpdateLatestVersionRequest,
) => Promise<UpdateLatestVersionResult>;

export interface UpdateCheckRequest {
  installedVersion?: string;
  cacheSeconds?: number;
  timeoutMs?: number;
  now?: () => number;
  statePath?: string;
  force?: boolean;
}

export interface UpdateCheckState {
  last_check_at: number;
  installed_version: string;
  latest_version: string;
  dismissed_versions: string[];
  last_fetch_failed_at?: number;
}

export interface UpdateCheckResult {
  state: UpdateCheckState;
  fetched: boolean;
  fetchFailed: boolean;
}

export type UpdateCheckFn = (
  request?: UpdateCheckRequest,
) => Promise<UpdateCheckResult>;

export interface UpdateInstallResult {
  output: string;
  errorOutput: string;
  code: number;
}

export type UpdateInstallFn = () => Promise<UpdateInstallResult>;

export interface UpdateRuntime {
  readInstalledVersion(): string;
  checkForUpdate(request?: UpdateCheckRequest): Promise<UpdateCheckResult>;
  installLatestPackage(): Promise<UpdateInstallResult>;
}
