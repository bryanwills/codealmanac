import os


def env_milliseconds(name: str, fallback: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return fallback
    try:
        parsed = int(value)
    except ValueError:
        return fallback
    if parsed <= 0:
        return fallback
    return parsed
