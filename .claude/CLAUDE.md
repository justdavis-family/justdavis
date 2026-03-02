# Agent Instructions

This file provides guidance to agents, such as [Claude Code](https://claude.ai/code),
  when working with code in this repository.

**Important**: Keep `CLAUDE.md` files evergreen;
  avoid adding point-in-time content to `CLAUDE.md` files,
  such as current sprint goals, active branches, temporary workarounds, etc.,
  that wouldn't make sense if multiple workstreams, PRs, or branches were in progress simultaneously.
Use `CLAUDE.md` files to document general principles, workflows, and architecture
  — not transient project state.

## What Is This Repository For?

The `justdavis.git` repository is an open source monorepo
  for the [@justdavis-family](https://github.com/justdavis-family/) org.
It consolidates open source projects to share infrastructure
  (documentation, build tooling, agent instructions, CI/CD)
  rather than spinning up a new repository for each project.

## How Is This Repository Organized?

The repository is roughly organized by domain,
  with different subtrees for different types of projects...

- `.claude/rules/`:
    shared agent rules and conventions,
    broken out by topic and/or file path/pattern;
    new agent rules belong here.
- `design/`:
    shared design documentation,
    including vision, requirements, principles, designs, and plans.

As sub-projects are added, they should be organized/grouped into directories by domain.

### How Do I Add a New Project to This Repository?

1. Create a project directory in the appropriate domain area.
2. Add a `mise.toml` with core tasks
    (`build`, `test`, `lint`, `dependencies:check`, `dependencies:update`, `ci`).
3. Update the root `mise.toml` to include the new project in `depends` arrays.
4. Add language-specific `.claude/rules/` files if needed
  a. For project-specific instructions,
       it's best to put them in `CLAUDE.md` files within the project directory.
5. Update the CI workflow if the project needs special runners or dependencies.
