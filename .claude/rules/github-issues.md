# GitHub Issue Workflow

Most issues exist for one of two reasons, and neither involves the design process:

- **Capture**: an idea, an annoyance, or a defect that shouldn't be lost.
- **Deferred work**: anything a PR consciously left undone,
    which [`pr-workflow.md`](pr-workflow.md) requires be tracked before that PR can merge.

Work that follows the design process is tracked differently — see
  [Design-Process Tracking Issues](#design-process-tracking-issues) below.

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

**Available issue templates:**
  [bug report](/.github/ISSUE_TEMPLATE/bug_report.md),
  [maintenance](/.github/ISSUE_TEMPLATE/maintenance.md),
  [delivery plan](/.github/ISSUE_TEMPLATE/delivery_plan.md),
  [milestone](/.github/ISSUE_TEMPLATE/milestone.md).

## Design-Process Tracking Issues

Work that follows the [design process](/design/README.md) is **not** mirrored into issues
  document-by-document.
There are no vision, requirement, engineering-design, or analysis issues.

A rough idea may well have a plain issue tracking it long before it has a delivery plan;
  that is fine and often useful.
What changes once a plan exists is that the work becomes concrete enough to track properly:
  a `Delivery Plan` issue with one `Milestone` sub-issue per milestone.
If a GitHub issue was already tracking the idea, it becomes that delivery-plan issue;
  otherwise one is created.

See [`design/delivery-plans/README.md`](/design/delivery-plans/README.md)
  for the reasoning behind those exclusions, the title formats,
  the issue-body structure, and how milestone sequencing is recorded.

## Metadata: Types, Labels, and Relationships

A metadata field earns its place when it answers a question nothing else already answers.
Most fields GitHub offers do not clear that bar, and are listed as unused below.

| Field | Used on | For |
|---|---|---|
| Issue type | Issues | What kind of thing this is. |
| Labels | Both | Change type on PRs; a few mechanical flags. |
| Sub-issues | Issues | Delivery plan → its milestones. |
| Relationships | Issues | Milestone sequencing. |
| Assignees | Both | Who is responsible. |

### Issue Types

Every issue carries one; PRs cannot, as GitHub does not offer types there.

- **`Bug`** — something is broken. Set by the bug-report template.
- **`Feature`** — a new capability, not yet broken down into deliverable work.
- **`Task`** — everything else, including maintenance and tooling. Set by the maintenance template.
- **`Delivery Plan`** and **`Milestone`** — the tracking issues described above.

### Labels

Three narrow categories; anything else gets no label.
Most *issues* carry none — their type already says what they are.

1. **Change type, on PRs only**: `feat`, `fix`, `docs`, `chore`, `ci`, `refactor`,
     mirroring the title prefix.
   See [Change Types](pr-workflow.md#change-types) for the vocabulary and the reasoning.
2. **Mechanical flags** that *do* something: `claude-review` triggers the Claude review workflow.
3. **Labels GitHub consumes**: `help wanted` and `good first issue` feed contributor-discovery pages.

### Sub-Issues, Relationships, and Assignees

Sub-issues and `blocked by` relationships are used **only** for delivery tracking —
  see [`design/delivery-plans/README.md`](/design/delivery-plans/README.md).
Express any other connection between issues as a sentence in the body saying *how* they relate.

Assign issues and PRs to whoever is responsible.
For PRs that is normally the author, set when the PR is opened; an unassigned PR reads as unowned.

### Deliberately Unused

Recorded so they don't get re-litigated on sight:
  **Priority**, **Effort**, **Start date**, and **Target date** (planning judgements that shift
  faster than a field can track, or schedule commitments that delivery plans avoid);
  **GitHub Milestones** (wrong granularity, and the name collides with delivery-plan milestones);
  and **Projects** boards (`gh issue list` already answers what a board would show at this scale).

Revisit if a concrete, repeated need appears — but not before.

## Linking Issues to PRs

- Reference related issues in PR descriptions using `#issue-number` syntax.
- Use closing keywords (`Fixes #123`, `Closes #456`) when the PR resolves an issue.
- Link to dependency issues when work builds on or requires other issues.
