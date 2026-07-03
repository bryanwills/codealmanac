from collections.abc import Mapping

from claude_agent_sdk import StreamEvent

from codealmanac.engine.harnesses.models import (
    HarnessEvent,
    HarnessEventKind,
    HarnessRunActor,
)
from codealmanac.integrations.harnesses.claude.raw import raw_message


def stream_event(
    message: StreamEvent,
    actor: HarnessRunActor,
) -> tuple[HarnessEvent, ...]:
    text = text_delta_from_stream_event(message.event)
    if text is None:
        return ()
    return (
        HarnessEvent(
            kind=HarnessEventKind.TEXT_DELTA,
            message=text,
            actor=actor,
            provider_event_id=message.uuid,
            provider_parent_tool_use_id=message.parent_tool_use_id,
            raw=raw_message(message),
        ),
    )


def text_delta_from_stream_event(event: Mapping[str, object]) -> str | None:
    if event.get("type") != "content_block_delta":
        return None
    delta = event.get("delta")
    if not isinstance(delta, Mapping):
        return None
    if delta.get("type") != "text_delta":
        return None
    text = delta.get("text")
    return text if isinstance(text, str) else None
