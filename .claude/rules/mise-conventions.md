---
paths:
  - "**/mise.toml"
---

# Mise Conventions

Conventions for `mise.toml` files in this monorepo.

## Structure

**One `mise.toml` per compilable unit.**
Nested projects get their own `mise.toml` if independently buildable.

## Core Required Tasks

Every project's `mise.toml` should include:

- `build` — Build the project (dev/debug profile).
- `test` — Run unit and integration tests.
- `lint` — Run all linters (language-specific + shellcheck for shell scripts).
- `dependencies:check` — Check for security vulnerabilities and outdated dependencies.
- `dependencies:update` — Update dependencies to latest compatible versions.
- `ci` — Complete CI suite (build → test + lint in parallel).

## CI Task Optimization

Structure CI tasks for parallel execution where possible:

```toml
[tasks.test]
depends = ["build"]
run = "<test command>"

[tasks.lint]
depends = ["build"]
run = "<lint commands>"

[tasks.ci]
depends = ["test", "lint"]
```

This creates: build → (test + lint parallel) execution.

## Task Composition Patterns

- Use `depends` for child tasks (runs in parallel by default).
- Use shell `&&` for sequential steps within a single task's `run`.
- Projects with code: build children first (`depends`), then own work (`run`).
- Projects without code: orchestrate children only (`depends`, no `run`).

## Shellcheck Integration

All lint tasks should include shellcheck if the project has shell scripts.
Each project maintains its own shellcheck paths to avoid overlap in the monorepo.

When creating/moving/deleting shell scripts:

- **Add scripts**: Add the path to shellcheck in the lint task.
- **Move scripts**: Update the path in the lint task.
- **Delete scripts**: Remove the path if no scripts remain.

## Adding a New Project

1. Create `mise.toml` with core tasks appropriate for the language/tooling.
2. Add shellcheck to lint task if project has shell scripts.
3. Update parent `mise.toml` to include new child in `depends` arrays.
4. Verify CI workflow uses mise tasks where applicable.

See [`.claude/CLAUDE.md`](/.claude/CLAUDE.md) for the full new-project checklist.
