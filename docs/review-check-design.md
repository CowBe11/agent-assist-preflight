# Review check design

Review checks are deliberately simple regex patterns. This keeps the helper dependency-free and easy to inspect.

## Naming

Use beginner-friendly product language:

- review check, not security rule
- review item, not finding
- priority, not severity
- confirm before running, not unsafe
- explanation, not alert

Compatibility fields may still use older names for now, but new docs and integrations should use the newer wording.

## Priorities

- `confirm`: stop and ask before running commands
- `review`: inspect before trying; prefer a disposable workspace or dry-run
- `note`: lower-impact context worth knowing

## Every check needs an explanation

Each check must include:

- `plain_language`: what the matched text probably means
- `why_it_matters`: practical reason a beginner might pause
- `beginner_next_step`: concrete next step before running commands

A bare category label is not enough. If a beginner cannot understand the output, the check is not finished.

## Pattern principles

1. Prefer readable, narrow patterns over clever broad ones.
2. Add fixtures for every new confirm-level check.
3. Include negation tests when common docs say things like "no token required".
4. Redact likely secret values before report output.
5. Do not claim runtime behavior from static text.
