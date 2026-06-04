# Contributing

Thanks for considering a contribution.

This project is a beginner-friendly preflight assistant, not a security scanner. Contributions should make review notes easier to understand and safer to act on.

Good first contributions:

- reduce false positives with narrowly scoped tests
- add new setup-review patterns with fixtures
- improve plain-language explanations
- improve beginner next steps
- document limitations more clearly

## Development loop

```bash
python3 -m unittest discover -s tests -v
python3 preflight_checker.py tests/fixtures/danger --format json --fail-on confirm
python3 preflight_checker.py . --format markdown --output self-preflight.md
```

Please add or update tests for review-check changes.

## Output wording rule

A category label alone is not enough. If a new check creates a review item, it must also include:

- what this means
- why it matters
- beginner next step
