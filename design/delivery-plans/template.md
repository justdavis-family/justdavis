# [Project Name] Delivery Plan

## Overview

What this plan sequences, and into how many milestones.
Link to the product requirements it delivers and the engineering design it follows.

State the **main delivery risk** and explain how the milestone ordering addresses it.
This is the most valuable paragraph in the document:
  it records *why* the sequence is what it is,
  which is exactly the reasoning that is otherwise lost.

Call out anything deliberately pushed to a late, optional milestone,
  and say plainly that the earlier milestones stand on their own without it.

## Delivery Conventions

Conventions that apply to every milestone in this plan.
Common ones:

- **Each milestone ships as its own merged PR.**
- **Public docs are built incrementally, alongside code, tests, and CI** — not deferred to the last
    milestone.
  Every milestone PR leaves the project's `README.md` accurate for the state of the project
    *at that point*.

## Milestones

Each milestone gets its own `###` heading, numbered `M1`, `M2`, ….
Milestones must be **thin vertical slices**:
  each one delivers something independently usable or testable,
  not an intermediate state that only makes sense in hindsight.
A good test is whether the reader could stop after any milestone
  and still have something worth having.

### M1 — [Short milestone title]

**Deliverable:** one or two sentences describing what a user, consumer, or contributor
  can actually do once this milestone merges.
Write it from their perspective, not the implementer's.

**Deferred:** what this milestone explicitly does *not* include,
  particularly anything a reader might otherwise assume is covered.

**In scope:**

- The concrete work needed to reach the deliverable above.
- Enough detail to bound the scope, but *not* an implementation recipe —
    the steps inside the PR are left to whoever does the work.
- Include tests, docs, and CI wiring as explicit scope items where they apply.

Scope bounds the work; it doesn't describe how the work is done.
Where the *how* matters for judging scope, **reference the relevant part of the engineering design**
  rather than restating it —
  the design is authoritative and evergreen,
  so a copy here will drift out of date and start contradicting it.

**Acceptance criteria:**

- [ ] The conditions that have to hold before this milestone is done.
- [ ] Write them so they can be checked off, and so someone other than the author could check them.
- [ ] Include the testing and documentation bars the milestone has to clear.

This checklist is **authoritative here, in the plan**.
The milestone's tracking issue carries a copy so progress can be ticked off as work proceeds,
  but the copy is a convenience — when the two disagree, this document is correct.

### M2 — [Short milestone title]

Repeat the `Deliverable` / `Deferred` / `In scope` / `Acceptance criteria` structure
  for each milestone.

### M[N] — [Short milestone title] (optional; may not be reached)

Mark genuinely optional milestones as such in the heading,
  and open the section by saying what makes them optional
  and confirming that the earlier milestones are fully usable without them.
Note any prerequisite that would have to be satisfied before the milestone could start
  (a paid account, an external dependency, a decision that hasn't been made yet).

## Explicitly Deferred (out of scope for this plan)

Work that is deliberately *not* in any milestone, with a brief reason for each.
This section prevents the plan from being read as an exhaustive roadmap,
  and it is where **honest deferral** happens:
  separate work that is required for the feature to function
  from nice-to-have polish, and be explicit about which this is.

Track anything here that needs to survive as actionable work
  in a GitHub issue, per [`.claude/rules/github-issues.md`](/.claude/rules/github-issues.md).

## References

- **Product Vision**: [Vision Title](../product-vision/YYYY-MM-DD-short-name.md).
- **Product Requirements**: [Requirement Title](../product-requirements/YYYY-MM-DD-short-name.md).
- **Engineering Design**: [Design Title](../engineering-designs/YYYY-MM-DD-short-name.md).
- **Analyses**: [Analysis Title](../analyses/YYYY-MM-DD-short-name.md).
