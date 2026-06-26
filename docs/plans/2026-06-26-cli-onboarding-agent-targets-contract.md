# CLI Onboarding Agent Targets Contract

Date: 2026-06-26

## Product Decision

`almanac setup` should start like OpenAlmanac setup: a beautiful terminal UI with
a vertical checklist for where Almanac should be installed.

The default path is:

1. Install agent instructions for selected global agent targets.
2. Install CLI auto-update by default.
3. Ask whether the user wants to handle automations themselves, default no.
4. If no, skip all local lifecycle machinery and point to the hosted dashboard.

## Final Onboarding Flow

```text
ALMANAC
a living wiki for codebases, for your agent

Where do you want to install Almanac?

[x] Claude Code
[x] Codex
[x] Cursor
[x] Windsurf
[x] OpenCode

[space] toggle  [up/down] move  [a] all  [enter] confirm  [q] quit
```

Then:

```text
Keep the Almanac CLI updated automatically? [Y/n]
```

Then:

```text
Do you want to handle automations yourself? [y/N]
```

## Default Branch

If the user answers no to self-managed automations:

```text
Agent instructions installed
CLI auto-update installed
Hosted updates -> codealmanac.com/dashboard
Setup complete
```

This branch must not:

- check Claude/Codex lifecycle readiness
- install sync automation
- install Garden automation
- ask auto-commit

## Self-Managed Automation Branch

If the user answers yes to self-managed automations:

1. Choose lifecycle agent.
2. Recommend Codex.
3. Choose model.
4. Recommend `gpt-5.5` for Codex.
5. Install local automations.
6. Ask auto-commit, default no.

The local automation install is equivalent to:

```bash
almanac automation install
```

That installs both scheduled jobs:

```text
sync    -> almanac sync --quiet 45m   every 5h
garden  -> almanac garden             every 4h
```

There should not be separate setup prompts for sync and Garden.

## Instruction Targets

TypeScript:

```ts
export type InstructionTargetId =
  | "claude"
  | "codex"
  | "cursor"
  | "windsurf"
  | "opencode";

export const DEFAULT_INSTRUCTION_TARGETS: readonly InstructionTargetId[] = [
  "claude",
  "codex",
  "cursor",
  "windsurf",
  "opencode",
];
```

Python reading:

```py
instruction_targets = [
    "claude",
    "codex",
    "cursor",
    "windsurf",
    "opencode",
]

default_instruction_targets = [
    "claude",
    "codex",
    "cursor",
    "windsurf",
    "opencode",
]
```

Target install contract:

TypeScript:

```ts
const INSTRUCTION_TARGETS = {
  claude: {
    label: "Claude Code",
    kind: "import",
    guidePath: "~/.claude/almanac.md",
    importPath: "~/.claude/CLAUDE.md",
  },
  codex: {
    label: "Codex",
    kind: "inline",
    path: "~/.codex/AGENTS.md",
  },
  cursor: {
    label: "Cursor",
    kind: "rule",
    path: "~/.cursor/rules/almanac/RULE.md",
  },
  windsurf: {
    label: "Windsurf",
    kind: "inline",
    path: "~/.codeium/windsurf/memories/global_rules.md",
  },
  opencode: {
    label: "OpenCode",
    kind: "inline",
    path: "~/.config/opencode/AGENTS.md",
  },
} as const;
```

Python reading:

```py
instruction_targets = {
    "claude": {
        "label": "Claude Code",
        "install": "write ~/.claude/almanac.md and import it from ~/.claude/CLAUDE.md",
    },
    "codex": {
        "label": "Codex",
        "install": "write managed inline block to ~/.codex/AGENTS.md",
    },
    "cursor": {
        "label": "Cursor",
        "install": "write ~/.cursor/rules/almanac/RULE.md",
    },
    "windsurf": {
        "label": "Windsurf",
        "install": "write managed inline block to ~/.codeium/windsurf/memories/global_rules.md",
    },
    "opencode": {
        "label": "OpenCode",
        "install": "write managed inline block to ~/.config/opencode/AGENTS.md",
    },
}
```

## Cursor Verification

Cursor global rules were verified on the user's machine by creating:

```text
~/.cursor/rules/almanac/RULE.md
```

with:

```md
---
alwaysApply: true
description: "Almanac global rule test"
---

When asked "almanac cursor global rule test", reply exactly:

loaded from global cursor rule
```

Cursor Agent loaded the rule and replied:

```text
loaded from global cursor rule
```

So Cursor is a valid global setup target.

## Setup Plan Contract

TypeScript:

```ts
export interface SetupPlan {
  instructionTargets: InstructionTargetId[];
  cliAutoUpdate: boolean;
  selfManagedAutomation: boolean;
  autoCommit: boolean;
}
```

Python reading:

```py
setup_plan = {
    "instruction_targets": selected_instruction_targets,
    "cli_auto_update": user_answer_or_default_yes,
    "self_managed_automation": user_answer_or_default_no,
    "auto_commit": user_answer_or_default_no if self_managed_automation else explicit_auto_commit_only,
}
```

Rules:

TypeScript:

```ts
async function buildSetupPlan(args: SetupPlanOptions): Promise<SetupPlan> {
  const instructionTargets = await resolveInstructionTargets(args);
  const cliAutoUpdate = await resolveCliAutoUpdate(args);
  const selfManagedAutomation = await resolveSelfManagedAutomation(args);
  const autoCommit = selfManagedAutomation
    ? await resolveAutoCommit(args)
    : resolveExplicitAutoCommit(args.options);

  return {
    instructionTargets,
    cliAutoUpdate,
    selfManagedAutomation,
    autoCommit,
  };
}
```

Python reading:

```py
def build_setup_plan(args):
    instruction_targets = resolve_instruction_targets(args)
    cli_auto_update = resolve_cli_auto_update(args)
    self_managed_automation = resolve_self_managed_automation(args)

    if self_managed_automation:
        auto_commit = resolve_auto_commit(args)
    else:
        auto_commit = resolve_explicit_auto_commit(args.options)

    return {
        "instruction_targets": instruction_targets,
        "cli_auto_update": cli_auto_update,
        "self_managed_automation": self_managed_automation,
        "auto_commit": auto_commit,
    }
```

## Setup Orchestration

Setup chooses the lifecycle agent only inside the self-managed automation branch.

TypeScript:

```ts
const plan = await buildSetupPlan({ out, interactive, options });

await runGuidesSetupStep({
  out,
  options,
  targets: plan.instructionTargets,
});

const globalInstall = await runGlobalInstallStep({ out, interactive, options });

if (plan.cliAutoUpdate) {
  await runAutoUpdateSetupStep(...);
}

if (plan.selfManagedAutomation) {
  const agentChoice = await chooseDefaultAgent({
    out,
    interactive,
    requested: options.agent,
    requestedModel: options.model,
    spawnCli: options.spawnCli,
  });

  await runAutomationSetupStep(...);
}

if (plan.selfManagedAutomation || plan.autoCommit || options.autoCommit === false) {
  await runAutoCommitSetupStep(...);
}
```

Python reading:

```py
plan = build_setup_plan(out, interactive, options)

install_agent_instructions(plan["instruction_targets"])

global_install = install_globally_if_needed()

if plan["cli_auto_update"]:
    install_cli_auto_update()

if plan["self_managed_automation"]:
    agent = choose_lifecycle_agent()  # Codex recommended
    model = choose_model(agent)       # gpt-5.5 recommended for Codex
    install_local_automations()       # sync + garden together

    configure_auto_commit(plan["auto_commit"])
else:
    skip_lifecycle_agent_check()
    skip_sync_cron()
    skip_garden_cron()
    skip_auto_commit_question()

if options.auto_commit is not None and not plan["self_managed_automation"]:
    configure_auto_commit(plan["auto_commit"])
```

## File Changes

### `src/cli/commands/setup/setup-plan.ts`

Add:

- `instructionTargets`
- `selfManagedAutomation`
- `resolveInstructionTargets`
- `resolveSelfManagedAutomation`

Change:

- `autoCommit` is only asked when `selfManagedAutomation` is true.
- explicit `--auto-commit` / `--no-auto-commit` still apply for compatibility.
- legacy explicit sync/Garden flags still force `selfManagedAutomation = true`.

TypeScript:

```ts
function hasExplicitLocalAutomationOptions(options: SetupOptions): boolean {
  return options.automationEvery !== undefined ||
    options.automationQuiet !== undefined ||
    options.gardenEvery !== undefined ||
    options.gardenOff === true;
}
```

Python reading:

```py
def has_explicit_local_automation_options(options):
    return (
        options.automation_every is not None
        or options.automation_quiet is not None
        or options.garden_every is not None
        or options.garden_off is True
    )
```

### `src/cli/commands/setup/instruction-target-choice.ts`

New file.

Responsibilities:

- render OpenAlmanac-style vertical checklist
- default-select every supported global target
- return selected `InstructionTargetId[]`
- support non-interactive defaults

### `src/agent/install-targets.ts`

Expand current Claude/Codex-only install to target-selected install.
Move Claude-specific file writing out of this file. `install-targets.ts` must
not contain product-specific install mechanics after this change; it should be
the registry/dispatcher for target agents.

TypeScript:

```ts
export async function installAgentInstructions(args: {
  targets: readonly InstructionTargetId[];
  claudeDir: string;
  codexDir: string;
  cursorDir: string;
  windsurfDir: string;
  opencodeDir: string;
  guidesDir: string;
}): Promise<AgentInstructionsChange> {
  for (const target of args.targets) {
    await installInstructionTarget(target, args);
  }
}
```

Python reading:

```py
def install_agent_instructions(args):
    for target in args["targets"]:
        install_instruction_target(target, args)
```

### `src/agent/instructions/cursor.ts`

New file.

Write:

```text
~/.cursor/rules/almanac/RULE.md
```

The file should be fully owned by Almanac, because it is target-specific.

Cursor rule body:

```md
---
alwaysApply: true
description: "Almanac instructions for Cursor"
---

<mini guide contents>
```

### `src/agent/instructions/claude.ts`

New file.

Move current Claude logic from `install-targets.ts` into this file.

Responsibilities:

- copy `guides/mini.md` to `~/.claude/almanac.md`
- copy `guides/reference.md` to `~/.claude/almanac-reference.md`
- add `@~/.claude/almanac.md` to `~/.claude/CLAUDE.md`
- remove those files/imports during uninstall
- check whether Claude instructions are present for doctor

`install-targets.ts` should call this module; it should not implement these
file operations directly.

### `src/agent/instructions/windsurf.ts`

New file.

Write/update managed block in:

```text
~/.codeium/windsurf/memories/global_rules.md
```

Use markers:

```text
<!-- almanac:start -->
...
<!-- almanac:end -->
```

### `src/agent/instructions/opencode.ts`

New file.

Write/update managed block in:

```text
~/.config/opencode/AGENTS.md
```

Use markers:

```text
<!-- almanac:start -->
...
<!-- almanac:end -->
```

### `src/cli/commands/setup/index.ts`

Change order:

1. print banner
2. build setup plan, including target picker
3. install selected agent instructions
4. global install step if needed
5. CLI auto-update step
6. if self-managed automation:
   - choose lifecycle agent/model
   - install sync + Garden automation
   - ask/configure auto-commit
7. print next steps

### `src/agent/readiness/view.ts`

Ensure lifecycle recommendation prefers Codex when possible.

The current code already prefers Codex if ready:

```ts
if (ready.includes("codex")) return "codex";
```

Keep that behavior. Tests should cover it.

### `src/agent/provider-id.ts`

Ensure Codex default model remains:

```ts
defaultModel: "gpt-5.5"
```

## Next Steps Copy

Default hosted branch:

```text
Next steps

1. Create or update your wiki from the dashboard:
   https://codealmanac.com/dashboard

2. Query locally once .almanac/ exists:
   almanac search "auth"
   almanac search --mentions <file>
```

Existing wiki branch:

```text
Next steps

1. Start querying it locally:
   almanac search --mentions <file>
   almanac search "auth"

2. Read one of the result pages:
   almanac show <result-slug>
```

Self-managed branch:

```text
Next steps

1. Local automations are running:
   almanac sync --quiet 45m
   almanac garden

2. Query locally:
   almanac search "auth"
   almanac search --mentions <file>
```

## Tests

Update or add:

- `test/setup-plan.test.ts`
- `test/setup.test.ts`
- `test/agents-command.test.ts` if install-target checks live there
- `test/provider-view.test.ts` for Codex recommendation

Required assertions:

- default setup installs Claude, Codex, Cursor, Windsurf, and OpenCode instructions
- default setup does not check lifecycle readiness
- default setup does not install sync plist
- default setup does not install Garden plist
- default setup does not ask auto-commit
- selecting Cursor writes `~/.cursor/rules/almanac/RULE.md`
- selecting Windsurf writes managed block to `~/.codeium/windsurf/memories/global_rules.md`
- selecting OpenCode writes managed block to `~/.config/opencode/AGENTS.md`
- self-managed yes installs both sync and Garden jobs
- self-managed yes asks/configures auto-commit with default no
- explicit legacy sync/Garden flags still enter self-managed automation path

## Out of Scope

- No new CLI commands.
- No project-local Cursor/Windsurf install.
- No hosted dashboard implementation.
- No separate sync/Garden prompts.
- No readiness checks on the default hosted branch.
