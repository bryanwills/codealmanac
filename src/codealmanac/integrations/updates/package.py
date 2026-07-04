import json
import subprocess
from importlib.metadata import PackageNotFoundError, distribution

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.maintenance.updates.models import (
    PACKAGE_NAME,
    PackageCommandResult,
    PackageInstallMetadata,
)


class InstalledPackageMetadataProvider:
    def read(self) -> PackageInstallMetadata:
        try:
            package = distribution(PACKAGE_NAME)
        except PackageNotFoundError:
            return PackageInstallMetadata(
                version="unknown",
                installer=None,
                editable=False,
                source_url=None,
            )
        direct_url = read_direct_url(package.read_text("direct_url.json"))
        return PackageInstallMetadata(
            version=package.version,
            installer=clean_optional_text(package.read_text("INSTALLER")),
            editable=direct_url.editable,
            source_url=direct_url.source_url,
        )


class SubprocessPackageCommandRunner:
    def run(self, command: tuple[str, ...]) -> PackageCommandResult:
        try:
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=False,
            )
        except OSError as error:
            return PackageCommandResult(
                exit_code=1,
                stderr=f"{error.__class__.__name__}: {error}",
            )
        return PackageCommandResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )


class DirectUrlMetadata(CodeAlmanacModel):
    editable: bool = False
    source_url: str | None = None


def read_direct_url(raw: str | None) -> DirectUrlMetadata:
    if raw is None:
        return DirectUrlMetadata()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return DirectUrlMetadata()
    if not isinstance(payload, dict):
        return DirectUrlMetadata()
    dir_info = payload.get("dir_info")
    editable = False
    if isinstance(dir_info, dict):
        editable = dir_info.get("editable") is True
    url = payload.get("url")
    return DirectUrlMetadata(
        editable=editable,
        source_url=url if isinstance(url, str) and url.strip() else None,
    )


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned == "":
        return None
    return cleaned
