# Security policy

Agent Assist Preflight is not a security scanner, not a sandbox, and not a safety guarantee. Its core preflight scanner turns setup text into review notes without executing commands from the project being inspected.

## Reporting a vulnerability

If you find a vulnerability in this helper itself, please open a private report if the repository host supports it, or open an issue that avoids publishing exploit details.

Do not include real API keys, tokens, passwords, private logs, or private candidate reports in public issues.

## Secret handling

- Never commit real `.env` files.
- Use `.env.example` with placeholder values only.
- Reports should mention secret key names, not secret values.
- The helper redacts likely secret values from excerpts, but users should still avoid scanning private secrets when possible.

## Scope boundary

The **project preflight scan** is read-only with respect to the project being inspected: it reads text files and does not execute commands found in README files, scripts, or configuration.

The local management WebUI has a slightly broader scope and should not be described as literally "no command execution / no writes":

- Environment diagnostics may run a small, fixed set of read-only inspection commands to query tool versions and listening ports.
- The WebUI may write its own local state, such as review comments, URL cards, command-confirmation cards, and command-card mode.
- Glossary candidate management intentionally edits the local candidate data file.
- The server is intended to bind only to `127.0.0.1` / `localhost`.

It must not install packages, execute commands taken from a scanned project, automatically fetch URLs found in scanned text, or expose the management API on a public interface by default.

Future hard-guard or command-wrapper features should remain opt-in, explicit, and documented separately.
