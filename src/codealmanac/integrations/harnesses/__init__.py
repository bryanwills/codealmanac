from codealmanac.integrations.harnesses.claude.adapter import ClaudeCliHarnessAdapter
from codealmanac.integrations.harnesses.codex.adapter import CodexCliHarnessAdapter
from codealmanac.services.harnesses.ports import HarnessAdapter


def default_harness_adapters() -> tuple[HarnessAdapter, ...]:
    return (ClaudeCliHarnessAdapter(), CodexCliHarnessAdapter())
