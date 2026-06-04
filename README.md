# Agent Assist Preflight

[日本語README](README.ja.md)

Agent Assist Preflight is a tiny, dependency-free, read-only helper for people who want to pause before running setup commands from an unfamiliar developer tool.

Use it before copying commands from a new CLI, MCP server, installer, AI agent tool, or developer utility. It reads README/config-style text and turns suspicious or high-impact setup instructions into plain-language review notes:

- what the line probably means
- why a beginner might want to pause
- what to ask or check next

![Agent Assist Preflight WebUI showing beginner-friendly review notes](docs/assets/webui-preview.png)

## What it does

Agent Assist Preflight scans local text files and looks for setup instructions that often deserve a second look: global installs, `curl | sh`, secrets, billing, daemons, agent config changes, command execution patterns, containers, local ports, browser automation, and similar topics.

When it finds a matching line, it explains the item in practical language:

```text
What this means: The text mentions tokens, passwords, API keys, OAuth, or .env files.
Why it matters: Secrets can be leaked into logs, shell history, screenshots, commits, or agent context.
Beginner next step: Use placeholder values while reading. Do not paste real secrets until you know where they are stored.
```

The target audience is:

- beginners trying developer tools, CLIs, installers, or MCP servers
- people who use AI coding agents and want a pause before setup steps
- agents/integrations that need a read-only preflight signal before proceeding

## What it does not do

This project is intentionally modest.

It is **not a security scanner**. It does **not** decide whether a project is safe. It does **not** sandbox, install, execute, fetch, or modify anything. It is a read-only preflight assistant that helps you slow down before running commands you do not understand yet.

## First: easiest way to try it

**Windows:** double-click `起動する.bat`. It requires Python 3, starts the local-only WebUI, and opens `http://127.0.0.1:8765/` in your browser.

**WSL / macOS / Linux:**

```bash
python3 management_webui/server.py
```

The browser UI lets beginners choose a local folder, inspect every review item, and copy the result when they want to ask ChatGPT or another person for help.

## CLI and integrations

The CLI is useful for agents, automation, and CI. Run it against a candidate project before copying setup commands from its README:

```bash
python3 preflight_checker.py path/to/candidate --format markdown
```

After package installation, use:

```bash
agent-assist-preflight path/to/candidate --format markdown
```

## Why this exists

Beginners and AI agents often hit the same problem:

> "The tool warned me, but I still do not know what the warning means."

Agent Assist Preflight tries to avoid that by avoiding bare warnings like `high risk: secrets_or_auth`. Instead, it adds beginner-facing explanations and next steps:

```text
What this means: The text mentions tokens, passwords, API keys, OAuth, or .env files.
Why it matters: Secrets can be leaked into logs, shell history, screenshots, commits, or agent context.
Beginner next step: Use placeholder values while reading. Do not paste real secrets until you know where they are stored.
```

## Design principles

- read-only by default
- no network access
- no dependency installation
- no candidate command execution
- no sandbox claims
- no safety guarantees
- Python standard library only
- explain before alarming
- default to soft assistance, not blocking

Future SecWall-inspired features should stay optional and explicit. The default mode should help users understand and decide; it should not silently take over their workflow.

## Quick start

```bash
python3 preflight_checker.py path/to/candidate --format markdown
python3 preflight_checker.py path/to/candidate --format json
python3 preflight_checker.py path/to/candidate --exclude 'tests/fixtures/**'
python3 preflight_checker.py path/to/candidate --fail-on confirm
```

Example:

```bash
python3 preflight_checker.py tests/fixtures/danger --format markdown
```

## Decisions

The report returns one of three decisions:

- `no_review_items_found`: no obvious review items were found; this is not a safety guarantee
- `review_before_trying`: review these items before trying the project
- `confirm_before_running`: stop and ask before running commands from this project

Review priorities:

- `confirm`: do not run yet without explicit confirmation
- `review`: inspect the instruction and prefer a disposable workspace/dry-run first
- `note`: lower-impact context that may still be useful

Compatibility note: older JSON fields such as `finding_count`, `max_severity`, `findings`, and `human_approval_categories` are still emitted for now, but new integrations should prefer `review_item_count`, `max_priority`, `review_items`, and `confirmation_categories`.

## What it currently looks for

Confirm-before-running checks include:

- destructive delete/reset commands
- global installs and `curl | sh` style setup
- token/password/API key/.env instructions
- billing/paid/subscription language
- daemon/cron/service setup
- agent/MCP/Hermes/Claude config mutation
- obvious command-execution patterns

Review-before-trying checks include:

- external network access
- filesystem writes
- containers/VMs
- common local ports
- browser automation/control

Note-level checks include:

- local file reads
- dry-run/read-only/preview hints

## Local management WebUI

A local-only review desk is available for planning and beginner-perspective feedback.

```bash
python3 management_webui/server.py
# then open http://127.0.0.1:8765/
```

The WebUI lets collaborators read the official plan, inspect key docs, view the current danger-fixture sample output, and record beginner-facing review comments. Comments are stored locally in `management_webui/data/review_comments.json`.

It binds to `127.0.0.1` by default and does not expose a public server.

## Output formats

Markdown:

```bash
python3 preflight_checker.py tests/fixtures/danger --format markdown
```

JSON:

```bash
python3 preflight_checker.py tests/fixtures/danger --format json
```

CI-style gate:

```bash
python3 preflight_checker.py tests/fixtures/danger --format json --fail-on confirm
```

Exit codes:

- `0`: completed; no configured failure threshold reached
- `2`: completed; configured `--fail-on` threshold reached

`--fail-on medium` and `--fail-on high` are kept as compatibility aliases for `review` and `confirm`.

## Beginner workflow

1. Run preflight against the candidate project.
2. Read the plain-language summary first.
3. For each review item, read:
   - `What this means`
   - `Why it matters`
   - `Beginner next step`
4. Do not paste real tokens, enter payment details, change agent config, start daemons, or run global installs until you understand the relevant review item.
5. Try first in a disposable folder or isolated workspace when possible.

See `docs/beginner-guide.md` for a longer walkthrough.

## Scope and limitations

This helper only reads text files below the paths you pass in. It does not:

- execute candidate commands
- install dependencies
- call package managers
- mutate MCP/Hermes/Claude/Codex config
- contact external services
- start browsers, daemons, or containers
- prove that a project is safe
- replace expert review, secret scanning, dependency auditing, or sandboxing

False positives and false negatives are expected.

See `docs/limitations.md`.

## Development

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Run the helper against itself:

```bash
python3 preflight_checker.py . --format markdown --output self-preflight.md
```

## Roadmap

This repo is meant to be the small, clean nucleus of a broader beginner-friendly agent assist kit:

- clearer review checks and examples
- beginner profiles and setup checklists
- command explainer mode
- scope planner for agent work: allowed read/write scope, forbidden paths, stop conditions
- optional SecWall-inspired hard guard wrapper, only when explicitly enabled
- optional SARIF/GitHub code scanning output
- optional MCP/Hermes/Claude/Codex-specific review check packs

## License

MIT.
