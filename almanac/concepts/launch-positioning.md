---
title: Launch Positioning
topics: [concepts, product]
sources:
  - id: repo-readme
    type: file
    path: README.md
    note: Public product tagline, local-first product surface, and command examples.
  - id: bookface-post
    type: file
    path: docs/launch/bookface-s26/post.md
    note: YC S26 Bookface launch draft and product narrative.
  - id: launch-assets
    type: file
    path: docs/launch/bookface-s26/assets/
    note: Final launch demo video and GIF assets.
  - id: openwiki-notes
    type: file
    path: docs/research/openwiki-launch-traction/notes.md
    note: OpenWiki launch traction research notes.
  - id: openwiki-export-script
    type: file
    path: docs/research/openwiki-launch-traction/fetch-github-stargazers.mjs
    note: Script that exports GitHub stargazers with starred timestamps and public profile fields.
  - id: openwiki-stargazers-csv
    type: file
    path: docs/research/openwiki-launch-traction/openwiki-stargazers.csv
    note: Exported OpenWiki stargazer data with one header row and 10,807 total lines in the current checkout.
  - id: tagit
    type: web
    url: https://github.com/liliang-cn/tagit
    note: GitHub repository for TagIt, an agent-in-team-chat comparison point.
  - id: agentchattr
    type: web
    url: https://github.com/bcurts/agentchattr
    note: GitHub repository for agentchattr, a local Slack-like agent chat comparison point.
---

# Launch Positioning

Launch positioning is the reusable product story behind CodeAlmanac launch work. The current line is that CodeAlmanac is a living wiki for a codebase, maintained by AI coding agents, with plain Markdown in `almanac/`, local indexes, Git review, and read commands such as `codealmanac search` and `codealmanac show` [@repo-readme]. Launch material should make that concrete as agent memory: coding agents start from zero, while CodeAlmanac preserves the decisions, gotchas, invariants, and flows they would otherwise rediscover [@bookface-post].

## Core Claim

The Bookface draft frames CodeAlmanac as open source, local, and free, then contrasts it with tools that make graphs or code search surfaces but do not maintain detailed connected Markdown articles from agent conversations [@bookface-post]. The skeptical-objection section should stay specific: the durable contrast is not "better docs"; it is conversation-updated Markdown in the repository, scheduled gardening, and an agent-native CLI read surface [@bookface-post] [@repo-readme].

The strongest example pattern is a future agent being asked to add Okta SSO and finding a previous WorkOS decision plus a webhook replay gotcha before coding [@bookface-post]. That example works because it names a concrete task, a concrete prior decision, and a concrete failure mode instead of only restating the product category.

## Demo Asset

The launch demo asset is a 35-second product video under `docs/launch/bookface-s26/assets/`, with MP4 and GIF versions present in the launch folder [@launch-assets]. The GIF asset is 17 MB in the current checkout, which leaves little headroom for platforms that recompress uploads [@launch-assets].

For demo structure, use [Demo CodeAlmanac in a launch video](../guides/demo-codealmanac-in-launch-video). That guide keeps the video centered on the served wiki as proof and the terminal query as the product payoff.

## Market Comparison Notes

OpenWiki research is raw launch analysis, not a final report. The useful reusable conclusion is that OpenWiki's early growth looked like a developer-viral open-source launch: the notes record about 9k GitHub stars in roughly a week, Trendshift daily rankings, HN activity, and LinkedIn/X repost waves, while also stating that exact referral sources are not public without repository-owner traffic data [@openwiki-notes]. A later export script fetched GitHub stargazers through GraphQL in `STARRED_AT` order with public profile fields such as login, location, company, bio, follower counts, and public repository count [@openwiki-export-script]. The current `openwiki-stargazers.csv` file has 10,807 total lines, including its header row [@openwiki-stargazers-csv].

The agent-chat comparison set from the July 8 lookup has two useful anchors. TagIt positions itself as a self-hosted chat interface where a team can `@mention` coding agents, register Claude Code and Codex CLIs, and route Slack or Feishu messages to the configured agent [@tagit]. agentchattr is the Slack-like local chat comparison: its README describes `@claude`, `@codex`, and other agent mentions, shared channels, and agent-to-agent wakeups through a local chat server [@agentchattr]. These tools are not direct wiki-memory substitutes, but they are relevant when launch copy mentions teams routing work to multiple agents.
