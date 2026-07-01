import base64
import binascii
from dataclasses import dataclass, field

from codealmanac.integrations.harnesses.codex.display import (
    codex_item_display,
    item_type_tool_name,
    tool_use_event,
)
from codealmanac.integrations.harnesses.codex.failures import (
    classify_codex_failure,
    failure_from_error_record,
)
from codealmanac.integrations.harnesses.codex.fields import (
    JsonObject,
    as_record,
    boolean_field,
    compact_json,
    first_present,
    number_field,
    string_array_field,
    string_field,
)
from codealmanac.integrations.harnesses.codex.usage import (
    parse_codex_app_server_usage,
)
from codealmanac.services.harnesses.models import (
    HarnessActorConfidence,
    HarnessActorRole,
    HarnessAgentTrace,
    HarnessEvent,
    HarnessEventKind,
    HarnessFailure,
    HarnessRunActor,
    HarnessToolStatus,
    HarnessUsage,
)


@dataclass
class CodexRunState:
    success: bool = False
    result: str = ""
    provider_session_id: str | None = None
    turns: int | None = None
    usage: HarnessUsage | None = None
    error: str | None = None
    failure: HarnessFailure | None = None
    root_thread_id: str | None = None
    root_turn_id: str | None = None
    result_source_thread_id: str | None = None
    result_source_turn_id: str | None = None
    result_source_role: HarnessActorRole | None = None
    agent_parents: dict[str, str | None] = field(default_factory=dict)
    agent_labels: dict[str, str] = field(default_factory=dict)
    completed_agents: set[str] = field(default_factory=set)


def map_codex_notification(
    notification: JsonObject,
    state: CodexRunState,
    is_root_completion: bool | None = None,
) -> tuple[HarnessEvent, ...]:
    method = string_field(notification, "method")
    params = as_record(notification.get("params"))
    thread_id = string_field(params, "threadId")
    turn_id = string_field(params, "turnId")
    actor = actor_for_codex_thread(state, thread_id)
    if state.provider_session_id is None and thread_id is not None:
        state.provider_session_id = thread_id

    if method == "item/agentMessage/delta":
        delta = string_field(params, "delta")
        if delta is None:
            return ()
        return (
            HarnessEvent(
                kind=HarnessEventKind.TEXT_DELTA,
                message=delta,
                actor=actor,
                raw=notification,
            ),
        )

    if method == "item/plan/delta":
        delta = string_field(params, "delta")
        if delta is None:
            return ()
        return (
            HarnessEvent(
                kind=HarnessEventKind.TOOL_SUMMARY,
                message=delta,
                actor=actor,
                raw=notification,
            ),
        )

    if method == "turn/plan/updated":
        summary = plan_summary(params)
        if summary is None:
            return ()
        return (
            HarnessEvent(
                kind=HarnessEventKind.TOOL_SUMMARY,
                message=summary,
                actor=actor,
                raw=notification,
            ),
        )

    if method == "thread/tokenUsage/updated":
        usage = parse_codex_app_server_usage(params.get("tokenUsage"))
        if usage is None:
            return ()
        state.usage = usage
        return (
            HarnessEvent(
                kind=HarnessEventKind.CONTEXT_USAGE,
                message=usage_message(usage),
                actor=actor,
                usage=usage,
                raw=notification,
            ),
        )

    if method == "item/started":
        item = as_record(params.get("item"))
        events = [
            tool_use_event(
                item,
                HarnessToolStatus.STARTED,
                actor,
                thread_id,
                turn_id,
            )
        ]
        events.extend(lifecycle_events(state, item, actor, "started"))
        return tuple(event for event in events if event is not None)

    if method == "item/completed":
        return map_completed_item(
            params,
            state,
            actor,
            thread_id,
            turn_id,
            notification,
        )

    if method in {
        "item/commandExecution/outputDelta",
        "command/exec/outputDelta",
        "item/fileChange/outputDelta",
    }:
        delta = output_delta(params)
        if delta is None or delta.strip() == "":
            return ()
        return (
            HarnessEvent(
                kind=HarnessEventKind.TOOL_SUMMARY,
                message=delta.strip(),
                actor=actor,
                raw=notification,
            ),
        )

    if method == "turn/completed":
        return map_turn_completed(
            params,
            state,
            actor,
            is_root_completion,
            notification,
        )

    if method == "warning":
        message = string_field(params, "message") or "Codex warning"
        return (
            HarnessEvent(
                kind=HarnessEventKind.TOOL_SUMMARY,
                message=f"Warning: {message}",
                actor=actor,
                raw=notification,
            ),
        )

    if method == "error":
        error = as_record(params.get("error"))
        failure = failure_from_error_record(error or params)
        state.success = False
        state.error = failure.message
        state.failure = failure
        return (
            HarnessEvent(
                kind=HarnessEventKind.ERROR,
                message=failure.message,
                actor=actor,
                failure=failure,
                raw=notification,
            ),
        )

    return ()


def map_completed_item(
    params: JsonObject,
    state: CodexRunState,
    actor: HarnessRunActor,
    thread_id: str | None,
    turn_id: str | None,
    notification: JsonObject,
) -> tuple[HarnessEvent, ...]:
    item = as_record(params.get("item"))
    if string_field(item, "type") == "agentMessage":
        text = string_field(item, "text")
        if text is None:
            return ()
        if actor.role == HarnessActorRole.ROOT:
            state.result = text
            state.result_source_thread_id = thread_id
            state.result_source_turn_id = turn_id
            state.result_source_role = actor.role
        events = [
            HarnessEvent(
                kind=HarnessEventKind.TEXT,
                message=text,
                actor=actor,
                raw=notification,
            )
        ]
        if actor.role == HarnessActorRole.HELPER and thread_id is not None:
            state.completed_agents.add(thread_id)
            events.append(
                HarnessEvent(
                    kind=HarnessEventKind.AGENT_COMPLETED,
                    message=text,
                    actor=actor,
                    agent_trace=HarnessAgentTrace(
                        parent_thread_id=state.agent_parents.get(thread_id),
                        child_thread_id=thread_id,
                        result=text,
                    ),
                    raw=notification,
                )
            )
        return tuple(events)

    display = codex_item_display(
        item,
        HarnessToolStatus.COMPLETED,
        thread_id,
        turn_id,
    )
    if display is None:
        return ()
    result_content = first_present(
        item.get("aggregatedOutput"),
        item.get("result"),
        item.get("error"),
    )
    is_error = display.status == HarnessToolStatus.FAILED or boolean_field(
        item, "success"
    ) is False
    events = [
        HarnessEvent(
            kind=HarnessEventKind.TOOL_RESULT,
            message=display.title or "Tool completed",
            actor=actor,
            tool_id=string_field(item, "id"),
            tool_name=item_type_tool_name(item),
            tool_display=display,
            tool_result=result_content,
            tool_is_error=is_error,
            raw=notification,
        )
    ]
    events.extend(lifecycle_events(state, item, actor, "completed"))
    return tuple(events)


def map_turn_completed(
    params: JsonObject,
    state: CodexRunState,
    actor: HarnessRunActor,
    is_root_completion: bool | None,
    notification: JsonObject,
) -> tuple[HarnessEvent, ...]:
    turn = as_record(params.get("turn"))
    error = as_record(turn.get("error"))
    error_message = string_field(error, "message")
    if error_message is not None:
        failure = classify_codex_failure(
            error_message,
            first_present(
                number_field(error, "statusCode"),
                number_field(error, "code"),
            ),
            error,
        )
        if is_root_completion is not False:
            state.success = False
            state.error = failure.message
            state.failure = failure
        return (
            HarnessEvent(
                kind=HarnessEventKind.ERROR,
                message=failure.message,
                actor=actor,
                failure=failure,
                raw=notification,
            ),
        )
    if is_root_completion is not False:
        state.success = True
        state.turns = 1
    return ()


def done_event(state: CodexRunState) -> HarnessEvent:
    status = "succeeded" if state.failure is None else "failed"
    result = state.result or state.error or "codex completed"
    return HarnessEvent(
        kind=HarnessEventKind.DONE,
        message=f"codex {status}: {result.splitlines()[0]}",
        provider_session_id=state.provider_session_id,
        usage=state.usage,
        failure=state.failure,
        source_thread_id=state.result_source_thread_id,
        source_turn_id=state.result_source_turn_id,
        source_role=state.result_source_role,
    )


def provider_session_event(thread_id: str) -> HarnessEvent:
    return HarnessEvent(
        kind=HarnessEventKind.PROVIDER_SESSION,
        message=f"codex provider session {thread_id}",
        provider_session_id=thread_id,
    )


def actor_for_codex_thread(
    state: CodexRunState,
    thread_id: str | None,
) -> HarnessRunActor:
    if thread_id is None:
        return HarnessRunActor(
            thread_id=None,
            role=HarnessActorRole.UNKNOWN,
            confidence=HarnessActorConfidence.UNKNOWN,
            label="Unknown actor",
        )
    if state.root_thread_id is None:
        state.root_thread_id = thread_id
    if thread_id == state.root_thread_id:
        return HarnessRunActor(
            thread_id=thread_id,
            role=HarnessActorRole.ROOT,
            confidence=HarnessActorConfidence.PROVIDER,
            label="Main",
        )
    return HarnessRunActor(
        thread_id=thread_id,
        role=HarnessActorRole.HELPER,
        parent_thread_id=state.agent_parents.get(thread_id) or state.root_thread_id,
        confidence=HarnessActorConfidence.PROVIDER,
        label=helper_label(state, thread_id),
    )


def lifecycle_events(
    state: CodexRunState,
    item: JsonObject,
    actor: HarnessRunActor,
    phase: str,
) -> tuple[HarnessEvent, ...]:
    if string_field(item, "type") != "collabAgentToolCall":
        return ()
    tool = string_field(item, "tool")
    sender_thread_id = string_field(item, "senderThreadId") or actor.thread_id
    receiver_thread_ids = string_array_field(item, "receiverThreadIds")
    if tool == "spawnAgent" and phase == "completed":
        events: list[HarnessEvent] = []
        for child_thread_id in receiver_thread_ids:
            state.agent_parents[child_thread_id] = sender_thread_id
            state.agent_labels[child_thread_id] = helper_label(state, child_thread_id)
            prompt = string_field(item, "prompt") or ""
            events.append(
                HarnessEvent(
                    kind=HarnessEventKind.AGENT_SPAWNED,
                    message=f"spawned {state.agent_labels[child_thread_id]}",
                    actor=actor,
                    agent_trace=HarnessAgentTrace(
                        parent_thread_id=sender_thread_id,
                        child_thread_id=child_thread_id,
                        prompt=prompt,
                        model=string_field(item, "model"),
                        reasoning_effort=string_field(item, "reasoningEffort"),
                    ),
                )
            )
        return tuple(events)
    if tool == "wait" and phase == "started":
        return (
            HarnessEvent(
                kind=HarnessEventKind.AGENT_WAIT_STARTED,
                message="waiting for helper agents",
                actor=actor,
                agent_trace=HarnessAgentTrace(
                    parent_thread_id=sender_thread_id,
                    child_thread_ids=receiver_thread_ids,
                ),
            ),
        )
    return ()


def helper_label(state: CodexRunState, thread_id: str) -> str:
    existing = state.agent_labels.get(thread_id)
    if existing is not None:
        return existing
    label = f"Helper {len(state.agent_labels) + 1}"
    state.agent_labels[thread_id] = label
    return label


def plan_summary(params: JsonObject) -> str | None:
    parts: list[str] = []
    explanation = string_field(params, "explanation")
    if explanation is not None:
        parts.append(explanation)
    plan = params.get("plan")
    if isinstance(plan, list):
        for item in plan:
            step = string_field(as_record(item), "step")
            if step is not None:
                parts.append(step)
    if len(parts) == 0:
        return None
    return " | ".join(parts)


def usage_message(usage: HarnessUsage) -> str:
    if usage.total_tokens is not None:
        return f"usage: {usage.total_tokens} tokens"
    return f"usage: {compact_json(usage.model_dump(mode='json', exclude_none=True))}"


def output_delta(params: JsonObject) -> str | None:
    delta = string_field(params, "delta")
    if delta is not None:
        return delta
    encoded = string_field(params, "deltaBase64")
    if encoded is None:
        return None
    try:
        return base64.b64decode(encoded).decode("utf-8", errors="replace")
    except (binascii.Error, ValueError):
        return encoded
