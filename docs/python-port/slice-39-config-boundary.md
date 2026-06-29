# Slice 39 - Config Boundary

## Scope

Add the local config service promised by the live agreement.

Implemented behavior:

- `services/config` owns local TOML parsing and precedence.
- User config path is `~/.almanac/config.toml`.
- Project config path is `.almanac/config.toml`.
- Project config wins over user config.
- CLI flags win over config.
- The first supported fields are:
  - `[harness].default = "claude" | "codex"`
  - `[sync].quiet = "45m"` or another `humanfriendly` duration string
- `ingest`, `garden`, `sync`, `sync status`, and `automation install` use
  `app.config` for lifecycle defaults.

## Out Of Scope

- No public `codealmanac config` command.
- No hosted/account config.
- No environment override system.
- No secret-management layer.
- No environment/dotenv/secrets source activation yet.

## Prior Art

- `pydantic-settings` provides first-class settings sources, including
  `TomlConfigSettingsSource`.
- `Dynaconf` is a broader layered configuration system. It is not needed while
  CodeAlmanac has only local TOML defaults and no environment/secrets contract.
- The service uses Pydantic Settings for TOML loading and validation, but it
  disables env, dotenv, and secret sources for v1 by returning only init-built
  sources from `settings_customise_sources(...)`.

## Cosmic Python Transfer

Chapter 13's composition-root guidance applies here. `app.py` wires
`ConfigService` once, and CLI dispatch receives the already-built app object.
The CLI does not construct config stores or parse TOML.

Chapter 4's service-layer guidance applies to ownership. Config loading is a
service use case, while CLI parsing remains an entrypoint concern.

## Verification

Focused checks:

```bash
uv run pytest tests/test_config_service.py tests/test_cli.py::test_cli_ingest_uses_configured_default_harness tests/test_cli.py::test_cli_sync_status_uses_configured_quiet_window tests/test_architecture.py
uv run ruff check src/codealmanac/services/config src/codealmanac/core src/codealmanac/app.py src/codealmanac/cli/main.py src/codealmanac/services/automation/service.py tests/test_config_service.py tests/test_cli.py tests/test_architecture.py
```

Full verification and dogfood are recorded in `verification-matrix.md`.
