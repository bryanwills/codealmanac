from codealmanac.integrations.harnesses.claude.adapter import ClaudeCliHarnessAdapter
from codealmanac.services.harnesses.ports import HarnessAdapter


def default_harness_adapters() -> tuple[HarnessAdapter, ...]:
    return (ClaudeCliHarnessAdapter(),)
