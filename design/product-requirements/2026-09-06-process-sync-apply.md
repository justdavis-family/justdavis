---
title: Apply a Process Sync Proposal
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-09-06-process-sync-proposal
extends: []
modifies: []
replaces: []
engineering_designs: []
prs: []
---

# Apply a Process Sync Proposal

## Summary

Having read a proposal from [Propose a Process Sync](2026-09-06-process-sync-proposal.md),
  a maintainer asks the same skill to carry it out in the repository they are working in
  — the *working repository* — for the changes the proposal addressed to that repository.
The skill turns each of those proposed pull requests into a branch and an open pull request there,
  with the source change's summary and provenance in the body,
  and leaves the maintainer to review and merge through the repository's normal workflow.
Changes the proposal addressed to the *counterpart repository* — the one the proposal was
  produced against — are not applied from here;
  the maintainer applies them by running the skill in that repository,
  with this one as its counterpart.

Every crossing between repositories therefore happens with a human present in the receiving
  repository, looking at the exact content, which is what keeps this requirement simple:
  it never needs a credential for any repository other than the one it runs in,
  and nothing it creates runs anywhere until the maintainer chooses to open it for review.

## User Story

As a maintainer who has read a process-sync proposal and decided what to do,
  I want the skill to open the proposed pull requests in the repository I am working in,
  so that converging on the current process is a review-and-merge task
  rather than a hand-copy of many files across a self-linked set of documents.

## Acceptance Criteria

### What Gets Applied, and Where

- [ ] Given a proposal, the skill applies only the pull requests the proposal addressed to the
        working repository;
        pull requests addressed to the counterpart are listed as "not applied here"
        with the instruction to run the skill there.
- [ ] The maintainer can apply the whole proposal or a chosen subset of its pull requests,
        and can defer or reject individual decisions the proposal raised
        without the skill applying a default in their place.
- [ ] A dry run shows exactly which branches and pull requests would be created, with their content,
        and creates nothing.
- [ ] Each applied pull request becomes one branch and one open pull request,
        based on and targeting the ref the proposal named,
        following the working repository's conventions for branches, titles, and descriptions.
- [ ] A grouped item in the proposal — the two halves of a content move,
        the files touched by one upstream change — lands in one pull request, never split across several.
- [ ] Renames land as renames, and removals as removals,
        so that history and links in the working repository stay coherent.
- [ ] Declared variation points carry the working repository's own value in the applied content.
- [ ] Only files the manifest classifies as process content are touched;
        the working repository's local content is byte-for-byte unchanged.
- [ ] Items the proposal marked as human-applied only are not applied;
        the skill lists them with the proposal's reason.
- [ ] If the working repository no longer matches the proposal — the target ref has moved on,
        a file the proposal expected is gone — the skill stops before creating anything
        and says what changed, rather than applying the parts that still fit.

### Provenance

- [ ] Each pull request's description says what the change is, where it originated
        (the counterpart as the maintainer supplied it, the ref, and the originating commits or
        pull requests), and why, quoting the source's own summary where one exists.
- [ ] Each pull request is individually revertible through the working repository's normal workflow.
- [ ] Applying the same proposal twice creates nothing the second time;
        the skill reports that the pull requests already exist and where.

### Nothing Crosses Unseen, Nothing Runs Unchosen

- [ ] The skill creates nothing the maintainer has not seen in that run:
        it shows what it is about to create, and creating it is the maintainer's explicit choice.
- [ ] When the working repository is public and a proposed change's content originates in a
        private repository, the skill shows the maintainer the complete diff that would be pushed
        and creates no branch or pull request until the maintainer explicitly confirms
        that specific content is safe to publish.
      Nothing the skill infers about the content — "it is only process content",
        "it is identical to something already public" — substitutes for that confirmation.
- [ ] When the working repository is public and a proposed change's content originates in a
        private repository, the pull request's description names that private repository, its ref,
        or its commits only if the maintainer chooses to include them;
        by default it says the change was synced from another repository that follows this process,
        and no more.
- [ ] The skill writes only to the working repository, and only as branches and pull requests
        that go through its normal review and merge;
        it does not approve, merge, or bypass branch protection.

### Documentation

- [ ] The skill's documentation covers applying a proposal: the whole-or-subset choice,
        the dry run, what the safe-to-publish confirmation looks like,
        and how to apply the counterpart's side.

## References

### Vision

- [One Development Process Across Many Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement makes a proposal actionable while keeping every crossing between repositories
    behind a human in the receiving repository;
    it delivers the vision's "review once on the merits, mechanical review per repository" metric
    and its privacy and containment metrics for the on-demand case.

### Engineering Design

- None yet.

### Analysis

- [Process Divergence Across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
    The shape of what will be applied first: mostly one repository adopting this one's current process,
    plus a short list of items flowing the other way.

### Engineering Principles

- [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md) —
    The skill writes only to the repository it runs in, and only through branches and pull requests;
    it needs no credential for any other repository.
- [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md) —
    A proposal that no longer matches the repository stops the skill before it creates anything,
    rather than applying what still fits.

### Related Requirements

- [Propose a Process Sync](2026-09-06-process-sync-proposal.md) —
    Produces the proposal this requirement applies; this requirement depends on it.

### Implementation

- None yet.
