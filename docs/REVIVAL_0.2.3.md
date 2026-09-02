# v0.2.3 Revival verification

Date: 2026-09-02

This note records the maintenance revival that converted the September audit findings into regression-tested fixes.

## Verified fixes

- Command-card IDs advance correctly from `cmdNNNN` history.
- Promoted glossary candidates persist locally and survive WebUI restarts.
- JSON POST requests have a 1.25 MB body limit.
- Cross-site browser POSTs to the localhost API are rejected; CLI/agent clients without an Origin header remain supported.
- Shell redirection, pipelines, chaining, and command substitution cannot inherit a low-risk classification from a safe-looking command prefix.
- The Windows compatibility launcher now delegates to the maintained management WebUI instead of carrying a stale duplicate server implementation.
- Package, CLI, launcher, management API, and README version labels are aligned to `0.2.3`.
- The HTTP path is genuinely compatible with Python 3.9 (`datetime.timezone.utc`).

## Verification

The final ordinary CI run on the revival branch passed all three jobs:

- core — Python 3.9
- core — Python 3.12
- pytest smoke/full suite

The dedicated regression suite exercises the audit findings, including live localhost HTTP 403/413 behavior.

## Remaining maintenance debt

The next substantial change should split `management_webui/server.py` by responsibility and replace the manually synchronized checked-in `dist/` copy with a generated distribution step.
