import httpx

from codealmanac.integrations.sources.web.models import FetchedWebResponse


def fetch_web_response(
    url: str,
    *,
    client: httpx.Client | None,
    max_bytes: int,
    timeout_seconds: int,
) -> FetchedWebResponse:
    if client is not None:
        return fetch_with_client(client, url, max_bytes, timeout_seconds)
    with httpx.Client(follow_redirects=True, timeout=timeout_seconds) as owned_client:
        return fetch_with_client(owned_client, url, max_bytes, timeout_seconds)


def fetch_with_client(
    client: httpx.Client,
    url: str,
    max_bytes: int,
    timeout_seconds: int,
) -> FetchedWebResponse:
    with client.stream(
        "GET",
        url,
        follow_redirects=True,
        timeout=timeout_seconds,
    ) as response:
        response.raise_for_status()
        body, truncated = read_bounded_response(response, max_bytes)
        content_type = response.headers.get("content-type", "").strip()
        return FetchedWebResponse(
            final_url=str(response.url),
            status_code=response.status_code,
            content_type=content_type or "(none)",
            body=body,
            response_truncated=truncated,
        )


def read_bounded_response(
    response: httpx.Response,
    max_bytes: int,
) -> tuple[bytes, bool]:
    chunks: list[bytes] = []
    total = 0
    truncated = False
    for chunk in response.iter_bytes():
        remaining = max_bytes - total
        if remaining <= 0:
            truncated = True
            break
        if len(chunk) > remaining:
            chunks.append(chunk[:remaining])
            truncated = True
            break
        chunks.append(chunk)
        total += len(chunk)
    return b"".join(chunks), truncated
