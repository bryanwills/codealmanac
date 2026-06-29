---
title: NPM Package Surface
summary: The published `codealmanac` package surface is controlled by `package.json`, and licensing changes must keep npm metadata, tarball contents, and README text in sync.
topics: [decisions]
sources:
  - id: package-metadata
    type: file
    path: package.json
    note: Defines the published npm metadata and the tarball `files` allowlist.
  - id: package-lock
    type: file
    path: package-lock.json
    note: Mirrors the root package license value.
  - id: readme
    type: file
    path: README.md
    note: Carries the public license badge and human-readable license section.
  - id: license-text
    type: file
    path: LICENSE.md
    note: Contains the canonical Apache 2.0 license text shipped in the package.
  - id: apache-license-commit
    type: commit
    rev: 0c2235a70e904b56d6bd864921107cb3599aebde
    note: Switched the package license to Apache-2.0 and removed the old commercial-license companion document from the published surface.
  - id: package-surface-session
    type: conversation
    path: /Users/kushagrachitkara/.codex/sessions/2026/05/20/rollout-2026-05-20T00-04-39-019e4433-6704-7e81-a624-e4355de08a72.jsonl
    note: Records the tarball-surface verification and the rule that licensing changes must update every published surface together.
verified: 2026-05-20
---

# NPM Package Surface

The published `codealmanac` package is defined by `[[./package.json]]`, not just by the repo tree. Changes to licensing therefore have two user-visible surfaces: package metadata and the tarball contents that `npm` distributes. [@package-metadata] [@package-surface-session]

## Current license state

Commit `0c2235a70e904b56d6bd864921107cb3599aebde` switched the package from `PolyForm-Noncommercial-1.0.0` to `Apache-2.0`. The current root metadata now reports `Apache-2.0` in `[[./package.json]]`, mirrors that value in the root package entry inside `[[./package-lock.json]]`, and points `[[./README.md]]` at Apache 2.0 in both the badge row and the License section. `[[./LICENSE.md]]` now contains the full Apache License 2.0 text. [@apache-license-commit] [@package-metadata] [@package-lock] [@readme] [@license-text]

The same change removed the old commercial-license companion document from the published surface. Before that commit, the `files` array in `[[./package.json]]` shipped both `LICENSE.md` and `COMMERCIAL.md`. The package now ships `LICENSE.md` only. [@apache-license-commit] [@package-metadata]

## Sync surface

When licensing changes again, future agents should treat these files as one review unit:

- `[[./LICENSE.md]]` for the authoritative license text
- `[[./package.json]]` for the npm `license` field and published `files` list
- `[[./package-lock.json]]` for the root package license mirror
- `[[./README.md]]` for the badge row and human-readable License section

Changing only one of those surfaces leaves the repo internally inconsistent. The package can otherwise claim one license in metadata, describe another in the README, or keep shipping stale auxiliary legal documents. [@package-surface-session]

## Verification

`npm pack --dry-run` is the direct check for this surface. It reports the exact tarball contents that would be published. On 2026-05-20, a dry run for `codealmanac@0.2.23` showed `LICENSE.md` and `README.md` in the tarball and did not include `COMMERCIAL.md`. [@package-surface-session]
