# Mise Usage

This project uses mise for tool, env, and task management.

## Experimental Monorepo Feature

`MISE_EXPERIMENTAL=1` is required for all `mise` commands
  to enable cross-project task references.
It cannot be set in `mise.toml` files directly;
  it must be set in the shell environment.

## Running Tasks

The absolute path from the monorepo root to a task in a specific project
  can be run with the `//<project>:<task>` syntax, e.g.:

```bash
MISE_EXPERIMENTAL=1 mise run '//cool_project:neat_project_task'
```

Or a task in the monorepo root can be run from within a subdirectory/project,
  using the `//:<task>` syntax, e.g.:

```bash
MISE_EXPERIMENTAL=1 mise run '//:neat_root_task'
```

Tasks in the current subdirectory/project can be run with the `:<task>` syntax, e.g.:

```bash
MISE_EXPERIMENTAL=1 mise run ':neat_cwd_task'
```

## Available Tasks

You can run `MISE_EXPERIMENTAL=1 mise tasks --all` to list all available tasks.

These are the main tasks available at the monorepo root:

- `//:build`: Build all projects.
- `//:lint:all`: Lint all projects.
- `//:test:all`: Test all projects.
- `//:ci`: Run full CI suite (build + test + lint).
- `//:ci:github:watch`: Watch GitHub PR checks.
- `//:install:hooks`: Install git hooks.
