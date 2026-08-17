<!--
Title this PR with a Conventional Commits type prefix, matching its branch prefix:
  feat: / fix: / docs: / chore: / ci: / refactor:
Scopes are encouraged in a monorepo, e.g. `docs(squawkbox): …`.
Assign yourself, and apply the matching type label.
See .claude/rules/pr-workflow.md for the full conventions.
-->

## Summary

1-3 sentences at a user-story level: *who* these changes are for, and *why*.
Then 1-3 bullets on *what* changed.

## Design Process

Link the `design/` documents this PR adds, modifies, or implements.
Write "N/A" for changes that don't go through the design process
(simple bug fixes, maintenance, infrastructure).

## Acceptance Criteria

_Delete this section unless this PR delivers a delivery-plan milestone._

Copy the milestone's acceptance criteria from the delivery plan and tick them off as you go.
The plan remains authoritative — if the two disagree, fix this copy.

- [ ] Criterion 1.
- [ ] Criterion 2.

## Success Criteria

- [ ] **All CI checks pass**: Tests pass, linting succeeds, formatting correct.
- [ ] **Code review recommendations addressed**: All review feedback implemented.
- [ ] **No stubbed/incomplete code**: All implementations are complete and tested.
- [ ] **No TODO/FIXME without tracking**: All TODOs tracked in GitHub issues with references.
- [ ] **Deferred work tracked in GitHub issues**: Any work deferred for future implementation
      must be tracked in GitHub issues with clear descriptions and acceptance criteria.
- [ ] **Follows Engineering Principles**: Code adheres to all
      [`design/engineering-principles/`](../design/engineering-principles/) or has documented
      (and reasonable) explanations for any divergences.

<!--
Add task-specific criteria for the kind of change this is — refactor, new feature,
bug fix, or documentation. See .claude/rules/pr-workflow.md for the standard sets.
-->

## Test Plan

How this was tested: commands run, tests added, manual verification performed.

## Context

Link related issues, and give any background a reviewer would otherwise lack.
Use closing keywords (`Fixes #123`) when this PR resolves an issue —
and take care not to write those keywords about issues this PR merely mentions.
