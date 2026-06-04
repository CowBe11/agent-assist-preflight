# Beginner guide

Agent Assist Preflight is for the moment before you run setup commands from a new project.

It does not tell you "safe" or "unsafe". Instead, it translates setup text into review notes you can understand.

## The three decisions

### `no_review_items_found`

No obvious review items were found in the scanned text.

This does not prove the project is safe. It only means this helper did not notice its known patterns.

Beginner next step:

- read the install instructions once more
- prefer commands that have dry-run, preview, or local-only modes
- avoid pasting secrets until you know where they go

### `review_before_trying`

The text mentions something worth checking before trying the project, such as network access, filesystem writes, containers, ports, or browser automation.

Beginner next step:

- read the surrounding README section
- try in a disposable folder first
- check whether a dry-run mode exists
- ask what data leaves your machine if network access is involved

### `confirm_before_running`

Stop before running commands from the project. The text mentions something beginners commonly regret doing too quickly: global installs, secrets, billing, daemons, config mutation, destructive commands, or command-execution patterns.

Beginner next step:

- do not paste real tokens yet
- do not enter payment details through an agent
- do not run sudo, global install, or curl-pipe-shell commands yet
- do not change agent/MCP/Hermes/Claude config until you know the exact file and rollback path
- ask a human or more capable agent to explain the matched line

## Reading one review item

Each item includes:

- Location: where the matched line came from
- Matched text: the exact text that triggered a review note
- What this means: plain-language translation
- Why it matters: the practical beginner-level reason to pause
- Beginner next step: what to do before running anything

Example:

```text
What this means: The setup may install software globally or run a downloaded install script.
Why it matters: Global installs and curl-pipe-shell commands can change your machine outside the project folder.
Beginner next step: Prefer a temporary folder, virtual environment, or local install. Ask before using sudo, -g, or curl | sh.
```

## Safe first-trial habits

Use these even when the report looks quiet:

- create a disposable test folder
- read scripts before running them
- prefer local installs over global installs
- use placeholder tokens while reading docs
- back up config files before changing them
- know how to stop background services before starting them
- keep real payment steps outside agent automation

## What this helper cannot do

It cannot inspect runtime behavior, dependency code, hidden install scripts, remote servers, browser sessions, or package contents. It only reads local text files and looks for review patterns.
