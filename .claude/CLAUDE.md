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

The repository's directory structure,
  and the steps for adding a new project to it,
  are documented in @CONTRIBUTING.md.

That document is canonical for both; don't restate either here.
Conventions that apply to humans and agents alike
  belong in the contributor-facing docs,
  because agents reliably read those but humans don't reliably read these.
