import type { CollectWikiHealthReport } from "./health.js";
import type { RegistryPathEquality } from "../../stores/wiki-registry/index.js";

export type { CollectWikiHealthReport };

export interface WikiDoctorOptions {
  cwd: string;
  registryPathEquals?: RegistryPathEquality;
  collectHealthReportFn?: CollectWikiHealthReport;
  now?: () => Date;
}

export type WikiDoctorCheckStatus = "ok" | "problem" | "info";

export interface WikiDoctorCheck {
  status: WikiDoctorCheckStatus;
  message: string;
  fix?: string;
  key: string;
}
