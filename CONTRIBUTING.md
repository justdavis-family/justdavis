# Contributing To This Project

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

## How Do I Get Started With Development?

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

Here is the current structure of the repository:

```
.github/     GitHub workflows and other config.
.claude/     Agent instructions and other config.
  rules/     Most agent instructions go here.
design/      Design documents, workflow, and related materials.
mise.toml    mise-en-place: dev env, tools, and tasks.
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

See [`design/README.md`](design/README.md)
  for the full design process
  and [`.claude/rules/pr-workflow.md`](.claude/rules/pr-workflow.md)
  for the full PR workflow.
As an intro to the process, here's the overview section from it...

> ## Design and Development Workflow Overview
>
> The design docs are used to drive and guide the development of new features and capabilities.
> These documents are generally created/updated either during or before their implementation.
>
> ```mermaid
> flowchart TB
>     subgraph design [Design Workflow]
>         direction LR
>         vision["Product Vision<br/>(why)"]
>         requirements["Product Requirements<br/>(what, atomic)"]
>         engineering-designs["Engineering Designs<br/>(how)"]
>         vision --> requirements --> engineering-designs
>     end
>
>     subgraph development [Development Workflow]
>         direction LR
>         plans["Implementation Plans<br/>(tasks)"]
>         pull-requests["Pull Requests"]
>         plans --> pull-requests
>     end
>
>     design --> development
> ```
>
> 1. The **Design Workflow** is...
>   1. [**Product Vision**](design/product-vision/README.md):
>      ensure that your goals/work align with a new or existing product vision,
>      which capture the high-level goals and direction for the product.
>   2. [**Product Requirements**](design/product-requirements/README.md):
>      break out each new feature or capability that you'll be implementing into product requirements,
>      which capture the user story and acceptance criteria for each feature.
>    Once fully implemented, Product Requirements are generally immutable,
>      with any divergences from earlier requirements being captured in _new_ Product Requirements,
>      mutually cross-linked with the ones that they supercede.
>   3. [**Engineering Designs**](design/engineering-designs/README.md):
>      capture any significant decisions that guide the architecture and design
>      of the projects, modules, and other components in the repository.
>    Should be evergreen: Engineering Designs should be updated as the system evolves.
>     1. [**Engineering Principles**](design/engineering-principles/README.md):
>        codify the higher-level, cross-cutting, or philosophical standards and norms
>        that all Engineering Designs, Implementation Plans, and code should align with.
> 2. The **Development Workflow** is...
>   1. [**Implementation Plans**](design/implementation-plans/README.md):
>      capture the detailed steps and tasks that are planned to implement a feature or capability.
>    These plans are ephemeral: they capture a specific plan at a specific point in time
>      and may change or be superceded as the implementation evolves.
>   2. [**Pull Requests**](.claude/rules/pr-workflow.md):
>      are used to prepare, review, and merge all changes
>      \— design documents, implementation plans, and the actual implementations \—
>      and this is enforced via the GitHub project's branch protection rules.
>    Note that, unless a PR's commits are very carefully curated,
>      they should generally be squashed before merging;
>      the `main` branch's commit history should tell a clear story of the project's evolution.

## What Other Conventions Should I Follow?

This repository's conventions and standards apply to both humans and agents,
  but are all codified for agent use:

1. [`.claude/CLAUDE.md`](.claude/CLAUDE.md):
     the overall, repository-wide conventions.
2. [`.claude/rules/`](.claude/rules/):
     more specific conventions, broken out by topic and/or file path/pattern.

In particular, the project's [**Engineering Principles**](design/engineering-principles/README.md)
  codify the higher-level, cross-cutting, or philosophical standards and norms
  that all Engineering Designs, Implementation Plans, and code should align with.

## What If I Encounter Issues or Have Questions?

If you encounter issues, you can either:

- **Ask a Question**: [Discussions](https://github.com/justdavis-family/justdavis/discussions).
- **Report an Issue**: [issues](https://github.com/justdavis-family/justdavis/issues).
