# Universal Agent Harness

Universal Agent Harness is a shared baseline for managing AI coding agents across Codex, Claude, and Gemini.

It keeps durable rules and automation in one common harness, then exposes tool-specific entry points through links and adapter config.

## What This Repository Is For

This repository is not an application project. It is a reusable operating layer for AI coding agents.

The goal is to make agent behavior:

- consistent across tools
- easy to inspect
- easy to strengthen over time
- safe to copy into other repositories
- testable as the harness grows

## Study Guide

If you want to understand the harness deeply before extending it, start here:

- [docs/HARNESS_GUIDE.ko.md](docs/HARNESS_GUIDE.ko.md)

That guide explains:

- what an agent harness is
- why this repository is structured this way
- what each file does
- which settings apply to Codex, Claude, and Gemini
- how the hooks work
- what is currently enforced versus only documented
- how to strengthen the harness safely

## Repository Layout

```text
.
├── AGENTS.md -> .agent-harness/rules/AGENT_GUIDE.md
├── CLAUDE.md -> .agent-harness/rules/AGENT_GUIDE.md
├── GEMINI.md -> .agent-harness/rules/AGENT_GUIDE.md
├── .claude/
│   └── settings.json -> ../.agent-harness/adapters/claude/settings.json
└── .agent-harness/
    ├── adapters/
    │   ├── claude/settings.json
    │   ├── codex/README.md
    │   └── gemini/README.md
    ├── hooks/
    │   ├── format_changed_file.py
    │   ├── run_tests.py
    │   └── tdd_guard.py
    └── rules/
        └── AGENT_GUIDE.md
```

## Design Principle

The root-level files are tool-facing entry points. They should stay small and stable.

The real source of truth lives under `.agent-harness/`:

- `.agent-harness/rules/` contains shared agent behavior rules.
- `.agent-harness/hooks/` contains shared automation scripts.
- `.agent-harness/adapters/` contains tool-specific configuration.

This prevents Codex, Claude, and Gemini instructions from drifting apart.

## Agent Entry Points

- Codex reads `AGENTS.md`.
- Claude Code reads `CLAUDE.md`.
- Gemini tooling commonly reads `GEMINI.md`.

All three point at the same guide, so policy changes happen in one place:

```text
.agent-harness/rules/AGENT_GUIDE.md
```

## Current Automation

Claude Code currently has the strongest native hook support, so `.claude/settings.json` links to the Claude adapter:

```text
.agent-harness/adapters/claude/settings.json
```

That adapter runs shared hook scripts after file edits:

1. `format_changed_file.py` formats changed files when Prettier or Black is available.
2. `run_tests.py` runs the detected test command.
3. `tdd_guard.py` warns when production code has no matching test file.

Codex and Gemini adapters are documented placeholders for now. Their shared operating rules are already active through `AGENTS.md` and `GEMINI.md`; tool-native hooks can be added under `.agent-harness/adapters/` as those tools expose stable project config.

## Validation

Run the harness self-tests with:

```bash
python3 -m unittest discover -s tests
```

Current tests verify:

- agent entry-point symlinks
- Claude settings symlink
- Claude adapter JSON validity
- TDD guard warning behavior
- TDD guard skip behavior when a matching test exists

## Strengthening Roadmap

Use this order when evolving the harness:

1. Add language-specific test and lint adapters.
2. Add tool-native config for Codex and Gemini when stable project hooks are available.
3. Add harness self-tests for hook scripts.
4. Add security checks for dangerous commands and secret leakage.
5. Add project templates for Python, Node, Go, Rust, and mixed repositories.

## Applying To Another Project

Copy the harness directory and create the agent entry-point links:

```bash
cp -r .agent-harness /path/to/project/
ln -s .agent-harness/rules/AGENT_GUIDE.md /path/to/project/AGENTS.md
ln -s .agent-harness/rules/AGENT_GUIDE.md /path/to/project/CLAUDE.md
ln -s .agent-harness/rules/AGENT_GUIDE.md /path/to/project/GEMINI.md
mkdir -p /path/to/project/.claude
ln -s ../.agent-harness/adapters/claude/settings.json /path/to/project/.claude/settings.json
```

If a filesystem does not support symlinks, copy the files instead and keep the copied files short pointers back to `.agent-harness/rules/AGENT_GUIDE.md`.
