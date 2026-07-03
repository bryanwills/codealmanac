from codealmanac.engine.harnesses.ports import HarnessAdapter
from codealmanac.integrations.harnesses.claude.adapter import ClaudeSdkHarnessAdapter
from codealmanac.integrations.harnesses.codex.adapter import (
    CodexAppServerHarnessAdapter,
)


def default_harness_adapters() -> tuple[HarnessAdapter, ...]:
    return (ClaudeSdkHarnessAdapter(), CodexAppServerHarnessAdapter())
