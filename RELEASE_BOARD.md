# Agent Assist Preflight — Release Board

## v0.2.3 "Revival" — 2026-09-02

The maintenance audit has been converted into a tested revival release candidate.

### Fixed in Revival

- [x] Package, CLI, management API, README, and compatibility-launcher versions aligned to `0.2.3`.
- [x] Command-card IDs correctly parse the `cmdNNNN` suffix instead of reusing `cmd0001`.
- [x] Promoted glossary candidates persist in local `glossary_overrides.json` and survive WebUI restarts.
- [x] Local JSON POST bodies are capped at 1.25 MB; oversized requests return HTTP 413.
- [x] Browser POSTs with a non-local Origin are rejected while CLI/agent clients without Origin remain supported.
- [x] Shell redirection, pipelines, command chaining, command substitution, and similar control operators cannot inherit a low-risk rating from a safe-looking prefix.
- [x] The old duplicated `standalone.py` server is replaced by a thin compatibility launcher for the maintained WebUI.
- [x] Root and checked-in `dist/` WebUI server copies remain synchronized.
- [x] Regression tests cover the audit findings.
- [x] CI runs core checks on Python 3.9/3.12 plus the full pytest suite.

### Current boundary

The scanner never executes commands found in an inspected project. The local management WebUI may run fixed read-only environment diagnostics and writes only its own local state. It does not auto-install dependencies, auto-send content to external services, or silently control the browser.

## Next — quality and maintainability

- [ ] Split `management_webui/server.py` by responsibility before the next large feature wave.
- [ ] Generate `dist/` from source instead of keeping a manually synchronized duplicate.
- [ ] Expand secret patterns for major cloud/chat providers.
- [ ] Improve mobile layout and accessibility.
- [ ] Add traceback highlighting and step-by-step common-error guidance.
- [ ] Add a small contributor guide and release checklist.

## Long term

- [ ] Local-AI assistance only behind explicit user action, masked text, confirmation UI, read-only tools, and no automatic external send.
- [ ] Stronger agent / MCP permission boundaries.
- [ ] Custom review patterns with a beginner-facing explanation for every rule.

## Out of scope

- Full security auditing or malware detection
- Real-time threat intelligence
- Automatic remote diagnosis
- Automatic command repair / execution
