import { startDetachedJobWorkerProcess } from "../../platform/jobs/worker-process.js";
import { startBackgroundJob } from "../../services/jobs/runtime/background-start.js";
import type {
  LifecycleOperationBackgroundStarter,
} from "../../services/lifecycle/index.js";

export const startCliBackgroundJob: LifecycleOperationBackgroundStarter =
  (options) =>
    startBackgroundJob({
      ...options,
      startWorker: startDetachedJobWorkerProcess,
    });
