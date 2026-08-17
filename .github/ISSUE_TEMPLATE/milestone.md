---
name: Milestone
about: Track one milestone from a delivery plan, delivered by a single PR
title: '<Project> M<N> — <milestone title>'
type: Milestone
assignees: ''
---

## Delivery Plan & Milestone

Link to the plan document in `design/delivery-plans/`, and name which milestone this tracks.
Set this issue as a sub-issue of that plan's issue.

## Deliverable

What a user, consumer, or contributor can actually do once this milestone merges.
Copy the plan's wording; keep it short.

## Blocked By

Any milestone that has to land first.
Record it with a `blocked by` issue relationship as well as noting it here,
so that queries for actionable work skip this issue until it's unblocked.

## Related Requirements

Link the requirement *documents* this milestone delivers, in whole or in part.
Requirements have no tracking issues, so there is nothing to link to in the tracker.

## Additional Context

Anything else worth knowing before starting the work.

---

Close this issue when its PR merges, noting the implementing PR number.
