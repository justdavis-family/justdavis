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
- Apply labels only where they earn their place — see [Labels](#labels) below.

**Available issue templates:** bug report, maintenance, delivery plan, milestone.

## Design-Process Tracking Issues

Work that follows the [design process](/design/README.md) is **not** mirrored into issues
  document-by-document.
Tracking starts only once the work is concrete and shippable —
  that is, once a delivery plan exists.
At that point the idea's original capture task becomes a `Delivery Plan` issue,
  with one `Milestone` sub-issue per milestone.
There are no vision, requirement, engineering-design, or analysis issues.

See [`design/delivery-plans/README.md`](/design/delivery-plans/README.md)
  for the reasoning behind those exclusions, the title formats,
  the issue-body structure, and how milestone sequencing is recorded.

## Labels

**A label earns its place when it answers a question nothing else already answers.**
That bar is deliberately high.
Tagging systems invite the opposite instinct — that every item deserves the "right" set of tags —
  and the result is a taxonomy nobody queries and everybody feels obliged to maintain.
Most issues and PRs need **no** labels at all, and that is the expected case, not an oversight.

Before applying a label, ask what search it would make possible.
If the answer is already visible in the title
  — a `docs:` or `fix:` prefix says the same thing a `documentation` or `bug` label would —
  the label is redundant, and redundant labels are the ones that rot.

Two labels do clear the bar:

- **`claude-review`** is *mechanical*, not descriptive:
    it triggers the Claude Code Review workflow on a PR.
  Apply it when you want that review.
- **`milestone`** marks a PR that delivers a milestone from a delivery plan.
  Issues express this with the `Milestone` issue *type*,
    but GitHub does not offer issue types on pull requests,
    so on the PR side this label fills that gap.
  It makes "which PRs delivered planned work, as opposed to ad-hoc changes"
    answerable when reconstructing a project's history.

The remaining labels exist for specific, narrow reasons:
  `bug` and `maintenance` are applied automatically by their issue templates,
  and `help wanted` and `good first issue` are surfaced by GitHub's own
  contributor-discovery pages.
Leave them to those uses rather than applying them by hand for tidiness.

## Assignees

Assign issues and PRs to whoever is actually responsible for them.
For PRs, that is normally the author, and it should be set when the PR is opened —
  an unassigned PR reads as unowned.

## Linking Issues to PRs

- Reference related issues in PR descriptions using `#issue-number` syntax.
- Use closing keywords (`Fixes #123`, `Closes #456`) when the PR resolves an issue.
- Link to dependency issues when work builds on or requires other issues.

## Issue Lifecycle

- Open issues represent planned or requested work.
- Closed issues document completed work or rejected proposals.
- Issues serve as the source of truth for project planning and history.
