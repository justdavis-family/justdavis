# Contributing to This Project

Welcome! We're glad you've wandered across this collection
  of small projects, home lab tooling, and other assorted experiments and resources.
The code and other resources here are open sourced in the hope of sharing knowledge
  — and on the off chance that others can directly use some of it.
If you _do_ find something here particularly enlightening or useful,
  please consider giving it a **star** on GitHub
  and letting us know about it over in the
  [discussions](https://github.com/justdavis-family/justdavis/discussions) section.

If you see something that is incorrect, or out of date, or otherwise needs improvement,
  please consider documenting it in a [new issue](https://github.com/justdavis-family/justdavis/issues/new)
  or submitting a correction in a [pull request](https://github.com/justdavis-family/justdavis/pulls).
The guidance below is intended to help you get started with that
  (and for our own reference).

## How Do I Get Started with Development?

[mise-en-place or "mise"](https://mise.jdx.dev/)
  is the dev tool, env, and task manager
  used for all of this repository's projects.
It's basically the developer front end for this repository,
  providing a unified CLI that handles building, testing, linting, etc.
See [mise](https://mise.jdx.dev/getting-started.html)
  for instructions on how to install and use it.

Once mise is installed,
  you can clone the repository and install the necessary git hooks,
  and then you're ready to get started with development:

```bash
git clone https://github.com/justdavis-family/justdavis.git justdavis.git
cd justdavis.git
MISE_EXPERIMENTAL=1 mise run 'install:hooks'
```

### How Do I Build and Test Locally?

The repo's top-level `:ci` task will build and test all projects (in the correct order):

```bash
MISE_EXPERIMENTAL=1 mise run ':ci'
```

## How Is This Repository Organized?

The repository is roughly organized by domain,
  with different subtrees for different types of projects.
Here is the current structure:

```
.github/               GitHub workflows, issue templates, and the PR template.
.claude/               Agent instructions and other config.
  rules/               Shared agent rules and conventions, by topic and/or path;
                         new agent rules belong here.
  skills/              Agent-invocable skills, one directory each.
design/                Design documents, workflow, and related materials.
github-analytics/      Collects GitHub repository analytics, and reports on them.
macos-focus-gopher/    Reports the current macOS Focus / Do Not Disturb state.
mise.toml              mise-en-place: dev env, tools, and tasks.
```

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

## What Workflow Is Used in This Repository?

Design documents drive and guide the development of new features and capabilities,
  and every change — design documents and implementations alike — lands through a pull request.
The two documents below are authoritative;
  read them rather than any summary of them:

- [`design/README.md`](design/README.md):
    the full design and development process.
  It covers what each type of design document is for,
    what order they're written in,
    and when the process can be skipped entirely
    (simple bug fixes, maintenance, and infrastructure changes go straight to implementation).
- [`.claude/rules/pr-workflow.md`](.claude/rules/pr-workflow.md):
    the full PR workflow.
  It covers branch naming, the required PR description outline,
    and how PRs get reviewed and merged.

## What Other Conventions Should I Follow?

This repository's conventions and standards apply to both humans and agents.
Most are codified for agent use, and live under `.claude/`:

1. [`.claude/CLAUDE.md`](.claude/CLAUDE.md):
     the overall, repository-wide conventions.
2. [`.claude/rules/`](.claude/rules/):
     more specific conventions, broken out by topic and/or file path/pattern.

Where a convention is just as relevant to humans,
  it should live in a contributor-facing document instead
  — this file, or something under [`design/`](design/) —
  and the `.claude/` files should point at it rather than restating it.

In particular, the project's [**Engineering Principles**](design/engineering-principles/README.md)
  codify the higher-level, cross-cutting, or philosophical standards and norms
  that all Engineering Designs, Delivery Plans, and code should align with.

## What If I Encounter Issues or Have Questions?

If you encounter issues, you can either:

- **Ask a Question**: [Discussions](https://github.com/justdavis-family/justdavis/discussions).
- **Report an Issue**: [issues](https://github.com/justdavis-family/justdavis/issues).
