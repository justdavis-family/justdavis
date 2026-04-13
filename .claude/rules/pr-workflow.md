# PR Workflow

This repository uses a **PR-based workflow** with branch protection rules enforced on main.

## Core Principles

- **ALL changes** must go through pull requests — direct commits to main are blocked.
- **ALWAYS** create a feature branch before making any code changes.
- **NEVER** attempt to commit directly to the main branch.

## Branch Naming Conventions

- `feature/descriptive-name` — New features or enhancements.
- `fix/descriptive-name` — Bug fixes.
- `refactor/descriptive-name` — Code refactoring without functional changes.
- `maintenance/descriptive-name` — Dependency updates and maintenance tasks.
- `docs/descriptive-name` — Documentation updates.

## Workflow Using gh CLI

1. Create and checkout a feature branch: `git checkout -b feature/your-feature-name`.
2. Make changes and commit to the feature branch.
3. Push branch: `git push -u origin feature/your-feature-name`.
4. Create PR: `gh pr create --title "Title" --body "Description"`.
5. Review and approve PR (self-review is acceptable, particularly for small changes).
6. Merge PR: `gh pr merge --squash` or `gh pr merge --merge`.
7. Branches are automatically deleted after merge (GitHub setting).

## PR Requirements

### Description Outline

The description for all PRs should have the following sections.

- **Summary**: 1-3 sentences explaining things at a user story level:
    _who_ the changes are for and the _why_ (i.e. the motivation).
  Follow that with 1-3 bullet points explaining _what_ changed.
- **Design Process**: Link to all of the `design/` process docs that the PR
    adds, modifies, and/or implements.
- **Success Criteria**: Include the success criteria checklist (see below).
- **Test Plan**: How the changes were tested (commands run, test coverage, manual verification).
- **Context**: Link to related issues or provide background for the change.

### Description Formatting

GitHub PR and issue descriptions and comments support GitHub Flavored Markdown,
  with one important difference:
  all line breaks are preserved.
Accordingly, our usual line-wrapping and continuation formatting rules should not be applied
  to PR or issue descriptions or comments.

### Success Criteria

**Every pull request must include a "Success Criteria" section** in the PR description.

### General Criteria (Required for All PRs)

- [ ] **All CI checks pass**: Tests pass, linting succeeds, formatting correct.
- [ ] **Code review recommendations addressed** — All review feedback implemented.
- [ ] **No stubbed/incomplete code**: All implementations are complete and tested.
- [ ] **No TODO/FIXME without tracking**: All TODOs tracked in GitHub issues with references.
- [ ] **Deferred work tracked in GitHub issues**: Any work deferred for future implementation
        must be tracked in GitHub issues with clear descriptions and acceptance criteria.
- [ ] **Follows Engineering Principles**: Code adheres to all `engineering-principles/` or has
        documented (and reasonable) explanations for any divergences.

#### Task-Specific Criteria

Add task-specific criteria based on the work being done.

**For refactoring PRs:**

- [ ] No functionality changes (existing tests still pass without modification).
- [ ] Test coverage maintained or improved.
- [ ] Performance benchmarks maintained or improved.

**For new feature PRs:**

- [ ] Feature documentation added to relevant docs.
- [ ] Tests added for main user workflows.

**For bug fix PRs:**

- [ ] Test added that reproduces the bug (fails before fix, passes after).
- [ ] Root cause documented in PR description or commit message.
- [ ] Related bugs checked for similar issues.

**For documentation PRs:**

- [ ] Markdown formatting follows project guidelines.
- [ ] All links verified working.
- [ ] Spelling and grammar checked.
