# GitHub Issue Workflow

Use GitHub issues to track all planned work, deferred features, and known bugs.

## Before Creating an Issue

- Search exhaustively for duplicate issues using multiple search terms.
- Check both open and closed issues for similar requests.
- If a related issue exists, comment on it or reference it
    rather than creating a duplicate.

## When Creating an Issue

- Use available issue templates for consistency.
- Write clear descriptions with context about why the work is needed.
- Include acceptance criteria or definition of done.
- Add appropriate labels for categorization.

**Available issue templates:** bug report, product requirement,
  product vision, maintenance.

## Design-Process Tracking Issues

Work that follows the [design process](/design/README.md) is tracked with a matching hierarchy of
  issues: a `vision` issue, a `requirement` issue, and — when there is a delivery plan —
  one `milestone` sub-issue per milestone.
The design documents stay authoritative for *content*;
  these issues are authoritative for *status*.

See [`design/delivery-plans/README.md`](/design/delivery-plans/README.md)
  for the title formats, labels, issue-body structure,
  and guidance on how requirements, milestones, and PRs correspond.

## Linking Issues to PRs

- Reference related issues in PR descriptions using `#issue-number` syntax.
- Use closing keywords (`Fixes #123`, `Closes #456`) when the PR resolves an issue.
- Link to dependency issues when work builds on or requires other issues.

## Issue Lifecycle

- Open issues represent planned or requested work.
- Closed issues document completed work or rejected proposals.
- Issues serve as the source of truth for project planning and history.
