# CodeRabbit GitHub App Flow

Research date: 2026-06-01

This note summarizes how CodeRabbit appears to work as a GitHub App and what the flow implies for an Almanac MVP where the first useful trigger is likely `pull_request.closed` with `merged: true`.

## Sources

- CodeRabbit GitHub installation guide: https://docs.coderabbit.ai/platforms/github-com
- CodeRabbit FAQ: https://docs.coderabbit.ai/faq
- CodeRabbit automatic review controls: https://docs.coderabbit.ai/configuration/auto-review
- CodeRabbit review commands: https://docs.coderabbit.ai/reference/review-commands
- CodeRabbit PR walkthroughs: https://docs.coderabbit.ai/pr-reviews/walkthroughs
- CodeRabbit self-hosted GitHub setup: https://docs.coderabbit.ai/self-hosted/github
- GitHub webhook events reference: https://docs.github.com/en/webhooks/webhook-events-and-payloads

## Installation and Authorization

CodeRabbit uses the normal GitHub App installation flow. A user logs in with GitHub, chooses a personal account or organization, then chooses either all repositories or selected repositories.

The GitHub.com guide says CodeRabbit needs owner-level permissions for at least one repository, and organization-owner permissions when installing into a GitHub organization. During installation, GitHub shows repository access scope and permissions before redirecting back to CodeRabbit.

The permissions visible in the docs match the install screen observed in this session:

- Read access: actions, checks, discussions, members, metadata
- Read/write access: code, commit statuses, issues, pull requests

The guide also says CodeRabbit requests code write access for review, issue management, and pull request generation features. For Almanac, that matters because a memory-update PR requires contents/write or a narrower alternative through a GitHub App installation token with contents write permission.

## Events and Triggers

CodeRabbit's public docs describe the user-facing trigger as:

- Automatically review a pull request when it is opened against the primary/default branch.
- Detect common primary branch names such as `main`, `master`, or `dev`.
- Allow configuration for target branches, draft PRs, labels, author exclusions, and related controls.
- Re-review on new pushes by default as incremental reviews.
- Allow manual review with PR comments.

The self-hosted GitHub setup lists the webhook events CodeRabbit recommends for its GitHub App:

- `meta`
- `issue_comment`
- `issues`
- `label`
- `public`
- `pull_request`
- `pull_request_review`
- `pull_request_review_comment`
- `pull_request_review_thread`
- `push`
- `release`

The core review loop probably depends on:

- `pull_request.opened` for first automatic review.
- `pull_request.synchronize` or `push` for incremental review after new commits.
- `pull_request.ready_for_review` when draft PRs become reviewable.
- `issue_comment.created` for commands such as `@coderabbitai review`.
- Review/comment/thread events for resolving, approving, or interacting with review threads.

The docs do not present a post-merge memory or documentation update flow. CodeRabbit is primarily PR-review and PR-assistance oriented, not a repository-memory maintenance bot.

## Configuration

CodeRabbit uses `.coderabbit.yaml` for repo-level behavior.

Important controls:

- `reviews.auto_review.enabled`: automatic review on/off.
- `reviews.auto_review.base_branches`: which target branches qualify; default includes the default branch.
- `reviews.auto_review.drafts`: draft PR inclusion; default is false.
- `reviews.auto_review.auto_incremental_review`: re-review new pushes; default is true.
- Keyword, label, and username filters can skip or opt into reviews.

The product lesson is that default behavior is automatic and broad, but users can dampen noise. For Almanac, defaults should be narrower: post-merge wiki update should be automatic, while PR/issue comments should be sparse and high-confidence.

## Manual Commands

Commands are sent as PR comments or PR-description markers with the `@coderabbitai` mention.

Important commands:

- `@coderabbitai review`: incremental review of new changes.
- `@coderabbitai full review`: full review from scratch.
- `@coderabbitai pause`: stop automatic reviews for the PR temporarily.
- `@coderabbitai resume`: restart automatic reviews.
- `@coderabbitai ignore`: place in PR description to disable automatic reviews for that PR.
- `@coderabbitai summary`: placeholder in PR description for summary placement.
- `@coderabbitai generate configuration`: create/export `.coderabbit.yaml`.
- `@coderabbitai help`: show command reference.

Almanac analogues:

- `/almanac update` or `@almanac update`: manually ask for a memory update from a merged PR or current PR.
- `/almanac note <text>`: maintainer-authored durable memory candidate.
- `/almanac ignore`: skip a PR.
- `/almanac config`: show resolved repo config.

For the first MVP, only `/almanac note` and perhaps `/almanac ignore` are worth considering. Manual commands are useful, but the main trigger should stay simple.

## What CodeRabbit Posts Back

CodeRabbit posts:

- A PR walkthrough comment at the top of the PR conversation.
- Inline review comments.
- Status messages when a review is skipped or cannot proceed.
- PR summaries, depending on configuration.
- Suggested labels and suggested reviewers.
- Optional generated artifacts such as sequence diagrams, docstrings, tests, and autofix commits.

The walkthrough can include:

- Changed files summary.
- Sequence diagrams.
- Estimated review effort.
- Related issues.
- Linked issue assessment.
- Related PRs.
- Suggested labels.
- Suggested reviewers.
- Review status messages.

For Almanac, the equivalent output should be much smaller:

- On merge: a memory PR, or no-op.
- On PR open/update: at most one context card if there is relevant existing memory.
- On maintainer command: an acknowledgement plus a memory PR.

## Concrete Almanac MVP Flow

The simplest GitHub App flow should not imitate full PR review. It should update the wiki after durable work lands.

Recommended MVP trigger:

1. User installs Almanac GitHub App on selected repositories.
2. Almanac subscribes to `pull_request` and `issue_comment`.
3. On `pull_request.closed`, if `merged: true` and target branch matches config, enqueue a memory-update job.
4. Worker fetches PR metadata, diff, commits, changed files, linked issues, review comments, and relevant existing `.almanac/` pages.
5. Worker runs the Almanac capture/update logic.
6. If no durable memory changed, do nothing.
7. If durable memory changed, open a separate "Memory PR" modifying `.almanac/pages/...` and/or `.almanac/topics.yaml`.
8. Human reviews and merges the memory PR.

Optional MVP command:

1. Maintainer comments `/almanac note <text>` or `@almanac note <text>` on a PR or issue.
2. `issue_comment.created` webhook enqueues a note-capture job.
3. Worker creates a Memory PR with the note grounded in the source comment.

## Deployment Implication

A true GitHub App needs a public HTTPS webhook receiver. GitHub sends webhook payloads to the app's configured URL. That means hosted Almanac needs at least:

- Webhook endpoint.
- Signature verification.
- Installation/repository state.
- Job queue.
- Worker that can fetch repo/PR context and create comments or PRs through installation tokens.

An Action-only prototype can avoid a hosted webhook server, but CodeRabbit's app-like UX comes from running hosted infrastructure behind the GitHub App.

## Design Takeaways for CodeAlmanac

- Do not start with full PR review. The sharper trigger is merged PR -> durable memory update.
- No-op should be common. Most PRs should not create wiki changes.
- Put behavior in repo config, analogous to `.coderabbit.yaml`, but keep the first config very small.
- Memory PRs are the core trust mechanism. They make the bot's output reviewable in Git.
- Use comments/commands as maintainer escape hatches, not the main workflow.
- Avoid noisy PR comments. CodeRabbit can afford frequent comments because review is the product; Almanac's value is durable memory, so the default should be quiet.
