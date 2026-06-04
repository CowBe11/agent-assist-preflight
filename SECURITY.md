# Security policy

Agent Assist Preflight is not a security scanner, not a sandbox, and not a safety guarantee. It is a read-only helper that turns setup text into review notes.

## Reporting a vulnerability

If you find a vulnerability in this helper itself, please open a private report if the repository host supports it, or open an issue that avoids publishing exploit details.

Do not include real API keys, tokens, passwords, private logs, or private candidate reports in public issues.

## Secret handling

- Never commit real `.env` files.
- Use `.env.example` with placeholder values only.
- Reports should mention secret key names, not secret values.
- The helper redacts likely secret values from excerpts, but users should still avoid scanning private secrets when possible.

## Scope boundary

The helper should remain read-only by default. Future hard-guard or command-wrapper features should be opt-in, explicit, and documented separately.
