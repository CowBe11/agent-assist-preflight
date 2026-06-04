# Limitations

Agent Assist Preflight is a read-only text-pattern helper. It is not a security product.

## It does not prove safety

A quiet report means only this:

> The helper did not find its known review patterns in the text it scanned.

It does not mean the project is safe, correct, trustworthy, or suitable to run.

## It only reads local text

The helper does not:

- clone repositories
- fetch URLs
- install packages
- execute scripts
- open browsers
- start containers
- inspect compiled binaries
- inspect package registry metadata
- audit dependencies
- monitor runtime behavior

## False positives are expected

A matched line may be harmless in context. For example, documentation may mention a dangerous command as something not to do.

The goal is not perfect classification. The goal is to create a useful pause and a readable explanation.

## False negatives are expected

The helper can miss risky instructions when wording differs from the built-in checks, when the behavior is hidden in code, or when setup pulls remote scripts that are not present locally.

## Beginner-safe wording rules

Project docs and output should avoid claiming:

- secure
- safe
- vulnerability detection
- protection
- sandboxing
- threat detection
- audit completeness

Prefer:

- review note
- preflight
- checklist
- confirm before running
- plain-language explanation
- beginner next step

## Optional hard guards are future work

SecWall-inspired command blocking may be useful later, but it should be explicit and opt-in. The default mode should remain read-only and non-blocking.
