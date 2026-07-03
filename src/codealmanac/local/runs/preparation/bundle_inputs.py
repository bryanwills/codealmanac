from collections.abc import Iterable

from codealmanac.engine.source_bundles.models import SourceBundleSessionInput
from codealmanac.local.control.models import SessionRecord


def source_bundle_session_inputs(
    sessions: Iterable[SessionRecord],
) -> tuple[SourceBundleSessionInput, ...]:
    return tuple(
        SourceBundleSessionInput(
            session_id=session.id,
            provider=session.provider.value,
            provider_session_id=session.provider_session_id,
            source_ref=session.source_ref,
        )
        for session in sessions
    )
