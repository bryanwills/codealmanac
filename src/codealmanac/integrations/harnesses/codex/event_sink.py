from codealmanac.engine.harnesses.models import HarnessEvent
from codealmanac.engine.harnesses.requests import HarnessEventSink


def record_harness_events(
    sink: HarnessEventSink | None,
    events: list[HarnessEvent],
    new_events: tuple[HarnessEvent, ...],
) -> None:
    for event in new_events:
        record_harness_event(sink, events, event)


def record_harness_event(
    sink: HarnessEventSink | None,
    events: list[HarnessEvent],
    event: HarnessEvent,
) -> None:
    events.append(event)
    if sink is not None:
        sink(event)
