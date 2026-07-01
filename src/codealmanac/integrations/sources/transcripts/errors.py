from codealmanac.services.sources.models import (
    SourceRef,
    SourceRuntime,
    SourceRuntimeStatus,
)


def unavailable_runtime(ref: SourceRef, title: str, diagnostic: str) -> SourceRuntime:
    return SourceRuntime(
        ref=ref,
        status=SourceRuntimeStatus.UNAVAILABLE,
        title=title,
        diagnostics=(diagnostic,),
    )
