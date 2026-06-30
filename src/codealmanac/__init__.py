from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]


def _installed_version() -> str:
    try:
        return version("codealmanac")
    except PackageNotFoundError:
        return "0+unknown"


__version__ = _installed_version()
