# Feature Questions

## Should `docs/almanac/` Be A Product Feature Or A Migration Mode?

The branch treats `docs/almanac/` as the new canonical location, not an optional
mode. That is the right product stance. A split-brain product where some repos
are "old Almanac" and some are "docs Almanac" would make prompts, docs, viewer,
and support harder.

Recommendation: keep legacy support as migration compatibility, not as an
ongoing product tier.

## Should The Viewer Keep `/getting-started`?

The current branch keeps it as a compatibility route. That is acceptable for
now, but the route name now conflicts with the Build prompt, which forbids
creating a second `getting-started.md`.

Recommendation: introduce a canonical front-door route later and keep
`/getting-started` only as a redirect or alias.

## Should Topic YAML Stay In Files?

Yes. The user's stated direction was to keep topics as YAML rather than making
the database authoritative. The branch follows that. SQLite should remain a
derived query projection.

Follow-up: add a dedicated migration command for topic files instead of relying
on implicit helper behavior.

## Should The Seed Section READMEs Count As Pages?

Yes for this repo, because they are real orientation pages in the new docs
surface. For `almanac build`, scaffold support pages are ignored only where they
are generic boilerplate. Section READMEs in a real repo should count as content
because they affect navigation and should block accidental rebuild without
`--force`.
