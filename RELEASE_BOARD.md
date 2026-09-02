# Agent Assist Preflight — Release Board

## Development snapshot — 2026-09-02

The repository has moved beyond the old `v0.1.2 (current)` board. Version labels are currently **not synchronized**, so do not cut a release until they are reconciled:

- `pyproject.toml` / CLI `VERSION`: `0.1.2`
- README banner: `v0.2.0 "Control Deck"`
- latest feature commit: `v0.2.2` candidate work

The latest implementation includes the bilingual Control Deck, a 144+ term glossary, candidate review workflow, fuzzy search, dark mode, URL cards, command-confirmation cards, environment diagnostics, and pytest smoke tests.

## Completed since the old v0.1.2 board

- [x] CLI error paste / secret redaction flow
- [x] Bilingual EN / JA dashboard
- [x] Glossary expansion to 144+ terms
- [x] Glossary candidate add / edit / reject / promote UI
- [x] URL handoff cards with blocked dangerous schemes
- [x] Command confirmation cards with risk assessment and modes
- [x] Tool / port diagnostics
- [x] Fuzzy glossary search
- [x] Dark mode
- [x] Pytest smoke-test suite
- [x] GitHub Actions CI for core tests
- [x] GitHub Actions job that actually runs the pytest suite (audit hardening branch)

## Before the next release — priority: high

- [ ] Synchronize the package, CLI, API, README, and release version labels.
- [ ] Fix command-card ID generation (`cmdNNNN` parsing can currently reuse `cmd0001`).
- [ ] Make glossary candidate promotion persist across a WebUI restart; the current implementation updates in-memory glossary dictionaries and removes the candidate from disk.
- [ ] Add a request-size limit to the local JSON API.
- [ ] Reject browser-originated cross-site requests to `/api/*` while preserving CLI / agent clients that do not send browser Origin headers.
- [ ] Ensure shell redirection / control operators cannot be classified as low-risk merely because a command starts with `echo`, `cat`, or another read-only-looking prefix.
- [ ] Decide and document the supported Python range for the WebUI separately from the core CLI if necessary.

## Priority: medium

- [ ] Split `management_webui/server.py` into smaller responsibilities before another large feature wave.
- [ ] Reduce duplicated source-of-truth risk between `management_webui/` and the checked-in `dist/` copy.
- [ ] Add regression tests for candidate promotion persistence and command-card ID rollover / history trimming.
- [ ] Add regression tests for hostile browser Origin / Referer requests to the localhost API.
- [ ] Expand secret patterns (AWS, Azure, GCP, Slack, Discord, etc.).
- [ ] Improve mobile layout.
- [ ] Add traceback line highlighting and step-by-step common-error guidance.

## Long term

- [ ] Local-AI assistance only behind an explicit user action, masked text, confirmation UI, read-only tools, and no automatic external send.
- [ ] Stronger agent / MCP permission boundaries.
- [ ] Custom review patterns with a clear beginner-facing explanation for every rule.

## Scope boundary

The core scanner reads project text and does not execute commands discovered in the inspected project. The management WebUI may run fixed read-only diagnostic commands and may write its own local state. See `SECURITY.md` for the current boundary.

Out of scope unless the project is deliberately re-scoped:

- Full security auditing or malware detection
- Real-time threat intelligence
- Automatic remote diagnosis
- Automatic command repair / execution
