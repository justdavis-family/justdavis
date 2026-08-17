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
- Apply metadata per the [Metadata](#metadata-types-labels-and-relationships) section below.

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

## Metadata: Types, Labels, and Relationships

GitHub offers a lot of metadata fields, and most of them we deliberately do not use.
The guiding rule is that **a field earns its place when it answers a question
  nothing else already answers.**
That bar is deliberately high:
  tagging systems invite the opposite instinct — that every item deserves the "right"
  set of tags — and the result is a taxonomy nobody queries
  and everybody feels obliged to maintain.

The short version:

| Field | Used on | For |
|---|---|---|
| Issue type | Issues | What kind of thing this is. |
| Labels | Both | Change type on PRs; a few mechanical flags. |
| Sub-issues | Issues | Delivery plan → its milestones. |
| Relationships | Issues | Milestone sequencing. |
| Assignees | Both | Who is responsible. |

### Issue Types

Every issue should carry a type; it is the primary way issues are categorized.
Pull requests cannot have one — GitHub does not offer types there.

- **`Bug`** — something is broken. Applied by the bug-report template.
- **`Feature`** — a new capability, not yet broken down into deliverable work.
- **`Task`** — everything else, including maintenance and tooling work.
- **`Delivery Plan`** and **`Milestone`** — the design-process tracking issues described above.

### Labels

Labels fall into exactly three narrow categories.
Anything that is not one of these does not get a label,
  and most *issues* carry none at all — their type already says what they are.

1. **Change type, on pull requests.**
   `feat`, `fix`, `docs`, `chore`, `ci`, `refactor` — mirroring the PR's title prefix.
   These duplicate the title on purpose;
     see [Change Types](pr-workflow.md#change-types) in the PR workflow for the vocabulary,
     the reasoning, and the automation that will maintain them.
   Do not apply these to issues, which use types instead.
2. **Mechanical flags** that *do* something rather than describe something.
   Currently just **`claude-review`**, which triggers the Claude Code Review workflow on a PR.
3. **Labels GitHub itself consumes.**
   **`help wanted`** and **`good first issue`** feed GitHub's contributor-discovery pages.

### Sub-Issues and Relationships

Both are used only for delivery tracking:
  milestone issues are sub-issues of their delivery-plan issue,
  and milestones that must land in order are linked with `blocked by` relationships.
See [`design/delivery-plans/README.md`](/design/delivery-plans/README.md)
  for how and why.

Don't reach for either outside that context.
A loose "related to" link between two issues is better expressed
  as a sentence in the issue body explaining *how* they relate.

### Assignees

Assign issues and PRs to whoever is actually responsible for them.
For PRs, that is normally the author, and it should be set when the PR is opened —
  an unassigned PR reads as unowned.

### Deliberately Unused

Recorded so that these don't get re-litigated every time someone notices them in the UI:

- **Priority, Effort, Start date, Target date** (org-level issue fields).
  Priority and effort are judged at planning time against everything else in flight,
    which is a moving target that a field on an issue cannot track.
  Dates imply a schedule commitment that delivery plans deliberately avoid —
    plans are sequences, not timelines.
- **GitHub Milestones** (the built-in grouping feature).
  Wrong granularity: our delivery milestones map to a single issue each,
    so a GitHub Milestone would group exactly one thing.
  The name collision with delivery-plan milestones would also be actively confusing.
- **Projects (boards).**
  Another surface to maintain, and `gh issue list` queries already answer
    what a board would show at this repo's scale.

Revisit any of these if a concrete, repeated need appears — but not before.

## Linking Issues to PRs

- Reference related issues in PR descriptions using `#issue-number` syntax.
- Use closing keywords (`Fixes #123`, `Closes #456`) when the PR resolves an issue.
- Link to dependency issues when work builds on or requires other issues.

## Issue Lifecycle

- Open issues represent planned or requested work.
- Closed issues document completed work or rejected proposals.
- Issues serve as the source of truth for project planning and history.
