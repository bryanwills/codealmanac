# Slice 116: Source Address Family Boundaries

## Scope

Keep source resolution behavior unchanged while splitting
`services/sources/address_resolution.py` by source-address family.

## Out of scope

- No new source kinds.
- No source syntax changes.
- No source runtime adapter changes.
- No CLI behavior changes.

## Design

Cosmic Python chapter 4 separates use-case orchestration from implementation
details, and chapter 3 favors small abstractions that hide messy details. The
current `SourcesService` is already clean, but `address_resolution.py` now owns
every address grammar at once.

Target shape:

```python
def resolve_address(address: SourceAddress, cwd: Path) -> SourceBrief:
    raw = address.raw
    if raw.startswith("github:"):
        return resolve_github_shorthand(raw)
    if raw.startswith("git:range:"):
        return resolve_git_range(raw)
    if raw == "git:diff" or raw.startswith("git:diff:"):
        return resolve_git_diff(raw)
    if raw.startswith("transcript:"):
        return resolve_transcript(raw)
    if is_http(raw):
        return resolve_url(raw)
    return resolve_path(raw, cwd)
```

`address_resolution.py` stays as the facade. Git, GitHub, web URL, local path,
transcript, prompt hints, and shared integer parsing move to modules named for
their reason to change.

## Verification

- Focused source service tests.
- Architecture guard for the facade and family modules.
- Isolated service dogfood resolving file, directory, missing path, Git,
  GitHub, transcript, and web inputs.
- Full pytest, Ruff, and diff hygiene.
