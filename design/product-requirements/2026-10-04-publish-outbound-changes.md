---
title: Publish Approved Outbound Changes
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-09-06-process-sync-apply
  - 2026-09-08-sync-decisions
  - 2026-10-04-unattended-sync-proposals
extends:
  - 2026-09-06-process-sync-apply
modifies: []
replaces: []
engineering_designs: []
prs: []
---

# Publish Approved Outbound Changes

## Summary

[Unattended Sync Proposals](2026-10-04-unattended-sync-proposals.md) ends with an approval request:
  a human in the *working repository* has looked at the complete diff of a change
  to this `justdavis` monorepo's development process
  and recorded that this exact content may go to the *counterpart repository*.
This requirement carries the change the rest of the way.
An approved change reaches the counterpart as something its maintainers review as real content,
  exactly as it was approved, and nothing runs there until one of them chooses to run it.

Two reviews bracket the crossing, and they answer different questions.
The approval in the working repository answers "may this leave?",
  which matters most when the working repository is private and the counterpart is public.
The review in the counterpart answers "should this land?",
  and it is a review of the content that actually arrived,
  not of anyone's description of it.
Neither stands in for the other.

Whether an approved change is carried across by a maintainer or by automation
  is for the engineering design, and depends on what can be shown to be safe.
What this requirement fixes is that the crossing is always *possible* by hand,
  and that however it happens, the same guarantees hold.

[Apply a Process Sync Proposal](2026-09-06-process-sync-apply.md) writes only to the repository
  it runs in; this requirement extends it with the one case where a change is delivered
  to the other repository, and with the approval that makes that acceptable.

## User Story

As a maintainer who has approved an outbound change,
  I want it to reach the counterpart as a change its maintainers can review,
  exactly as I approved it,
  so that an improvement made in this repository reaches the others without my hand-copying it,
  and without anything leaving or running that a human has not agreed to.

## Acceptance Criteria

### From Approval to the Counterpart

- [ ] An approved outbound change reaches the counterpart as a proposed change there,
        with the title, description, and content the approval request showed.
- [ ] Nothing about a change reaches the counterpart before its approval is recorded:
        not its content, not a draft of it, and not a description of it.
- [ ] What reaches the counterpart is exactly the content that was approved.
- [ ] If the content would differ from what was approved
        — the proposal was regenerated, or the counterpart has moved on —
        the approval lapses and a new one is sought before anything is published.
- [ ] An approval can be withdrawn at any time before the change is published.
- [ ] A refused request is never published.
- [ ] A maintainer can always publish an approved change themselves, by hand;
        no automation is required for this requirement to be met.

### Review in the Counterpart

- [ ] The published change goes through the counterpart's normal review and merge;
        publishing does not approve it, merge it, or bypass branch protection.
- [ ] The counterpart's review is of the content that actually arrived.
- [ ] Nothing in the published change — a workflow, a build, a test —
        executes in the counterpart until a human there has reviewed it and chosen to run it.
- [ ] Changes the proposal marked as human-applied only are never published by automation;
        the approval request says that a maintainer must carry them across.

### Privacy

- [ ] By default the published change says only that it was synced from another repository
        that follows this process;
        it names the working repository, its refs, or its commits
        only if the approver chose to include them.
- [ ] When the working repository is private and the counterpart is public,
        nothing about the published change identifies the working repository,
        including the name or account under which it arrives.
- [ ] An approval recorded on the request counts as the safe-to-publish confirmation that
        Apply a Process Sync Proposal requires for that exact content;
        the maintainer is not asked a second time unless the content has changed.

### Containment

- [ ] Publishing does not require the working repository to hold any credential that would allow
        an attacker who acquires it to automatically compromise another repository.
- [ ] The counterpart is not required to hold any credential, or to run anything,
        on the working repository's behalf.

### Closing the Loop

- [ ] The approval request records what was published and where it can be found in the counterpart.
- [ ] Publishing the same approved change a second time creates nothing.
- [ ] Once the change lands in the counterpart, the approval request is closed.
- [ ] If the counterpart's maintainers turn the change down, that outcome is recorded per
        [Remember Sync Decisions](2026-09-08-sync-decisions.md),
        and the same change is not put forward again.

### Documentation

- [ ] The process documentation covers the outbound path end to end:
        approving, withdrawing, publishing by hand, what the counterpart's maintainers see,
        and what a maintainer of a private repository must check before approving.

## References

### Vision

- [One Development Process across Many Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement delivers the outbound half of "improvements flow in both directions",
    under the vision's "private stays private" and "compromise stays contained" metrics:
    nothing is made visible in a public repository before a human confirms it,
    and nothing forwarded executes unreviewed.

### Engineering Design

- None yet.

### Analysis

- [Process Divergence across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
    The outbound changes already waiting: two corrections to this repository's own content,
    an engineering principle, and a workflow, none of which ever made the crossing.

### Engineering Principles

- [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md) —
    Publishing delivers one approved change to one repository for review, and can do nothing else there.
- [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md) —
    An approval that no longer matches its content lapses, rather than being stretched to cover
    something its approver never saw.

### Related Requirements

- [Unattended Sync Proposals](2026-10-04-unattended-sync-proposals.md) —
    Produces the approval requests this requirement acts on; this requirement depends on it.
- [Apply a Process Sync Proposal](2026-09-06-process-sync-apply.md) —
    Writes only to the repository it runs in;
    this requirement extends it to deliver an approved change to the counterpart.
- [Remember Sync Decisions](2026-09-08-sync-decisions.md) —
    Records a change the counterpart turned down; this requirement depends on it.

### Implementation

- None yet.
