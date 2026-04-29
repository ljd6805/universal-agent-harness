# Universal Agent Instructions

This file is the shared working guide for Codex, Claude, Gemini, and other coding agents in this repository.

## Purpose

This repository uses a universal harness so agent behavior can be managed, audited, and strengthened over time without duplicating rules across tools.

Tool-specific entry points should point here:

- `AGENTS.md` for Codex
- `CLAUDE.md` for Claude Code
- `GEMINI.md` for Gemini

## Core Workflow

### 1. Inspect Before Editing

Before changing files:

- Read the relevant files first.
- Check the repository status when git is available.
- Identify whether existing user changes are present.
- Preserve unrelated user changes.

### 2. Use TDD By Default

Production code should be driven by a failing test first.

```text
write failing test -> confirm failure -> minimal implementation -> confirm pass -> refactor
```

Acceptable exceptions:

- Documentation-only changes
- Configuration-only harness changes
- Exploratory scaffolding explicitly requested by the user
- User-approved exceptions

Test naming conventions:

- Python: `test_<name>.py` or `<name>_test.py`
- TypeScript or JavaScript: `<name>.test.ts`, `<name>.spec.ts`, `<name>.test.js`, or `<name>.spec.js`

### 3. Consider Parallelization

At task start, decide whether work can be split safely.

Parallelize only when:

- Different files or modules can be changed independently.
- Failures have separate causes.
- Research, implementation, and verification can proceed without shared mutable state.

Stay single-threaded when:

- Failures are related.
- Debugging requires a whole-system view.
- Multiple edits target the same file or tightly coupled behavior.

### 4. Verify Before Completion

Before reporting completion:

- Run the most relevant tests or checks available.
- If no tests exist, perform a concrete manual or script-level check.
- If verification cannot run, state the blocker and the command that should be run next.

### 5. Keep The Harness Maintainable

- Keep shared rules in `.agent-harness/rules/`.
- Keep shared automation in `.agent-harness/hooks/`.
- Keep tool-specific config in `.agent-harness/adapters/<tool>/`.
- Keep root-level agent files as pointers to the shared guide.
- Prefer small, auditable scripts over large inline shell commands.

## Current Shared Hooks

The shared hook scripts are:

- `.agent-harness/hooks/format_changed_file.py`
- `.agent-harness/hooks/run_tests.py`
- `.agent-harness/hooks/tdd_guard.py`

Adapters may call these scripts when the tool supports project hooks.
