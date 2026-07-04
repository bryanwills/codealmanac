from importlib import resources


def read_agent_guide() -> str:
    resource = resources.files("codealmanac.cloud.setup").joinpath("agent-guide.md")
    return resource.read_text(encoding="utf-8").strip() + "\n"
