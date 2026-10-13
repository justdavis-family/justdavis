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
engineering_designs:
  - 2026-10-13-process-sync
prs: []
---

# Apply a Process Sync Proposal

## Summary

Having read a proposal from [Propose a Process Sync](2026-09-06-process-sync-proposal.md),
  a maintainer asks the same skill to carry it out in the repository they are working in
  — the *working repository* — for the changes the proposal addressed to that repository.
The skill turns each of the proposal's units into a branch and an open pull request there,
  with the source change's summary and provenance in the body,
  and leaves the maintainer to review and merge through the repository's normal workflow.
Changes the proposal addressed to the *counterpart repository* — the one the proposal was
  produced against — are not applied from here;
  the maintainer applies them by running the skill in that repository,
  with this one as its counterpart.

Every crossing between repositories therefore happens with a human present in the receiving
  repository, looking at the exact content.
That is what keeps this requirement simple:
  the skill needs no credential for any repository other than the one it runs in,
  and nothing it creates runs anywhere until the maintainer, having seen its content,
  confirms its creation.

## User Story

As a maintainer who has read a process-sync proposal and decided what to do,
  I want the skill to open the proposed pull requests in the repository I am working in,
  so that converging on the current process is a review-and-merge task
  rather than a hand-copy of many files across a self-linked set of documents.

## Acceptance Criteria

### What Gets Applied, and Where

- [ ] The skill applies only the units the proposal addressed to the working repository;
        units addressed to the counterpart are listed as "not applied here",
        with the instruction to run the skill there.
- [ ] The maintainer can apply the whole proposal or a chosen subset of its units.
- [ ] The maintainer can defer or reject any decision the proposal raised;
        the skill applies no default in their place.
- [ ] The maintainer can ask for units to be combined and/or regrouped
        into a different set of pull requests.
- [ ] However the maintainer regroups, no pull request leaves the working repository inconsistent
        on its own: the two halves of a rename, or of a content move, stay together.
- [ ] A dry run shows exactly which branches and pull requests would be created, with their content,
        and creates nothing.
- [ ] Units the proposal marked as human-applied only are never written by automation:
        each is carried in its pull request, with the proposal's reason,
        in a form a maintainer can review and apply by hand, such as a patch.
      The carrier is for the maintainer to apply and remove before the pull request merges,
        and one left behind is a difference the next comparison reports.
- [ ] If the working repository no longer matches the proposal
        — the target ref has moved on, a file the proposal expected is gone —
        the skill stops before creating anything and says what changed.

### What Each Pull Request Contains

- [ ] Each applied unit becomes one branch and one open pull request,
        based on and targeting the ref the proposal named,
        and following the working repository's conventions for branch names, titles,
        and descriptions.
- [ ] Renames land as renames, so that the repository's history follows the file;
        removals land as removals.
- [ ] Declared divergences are preserved: the working repository's own values stay in place,
        and a part adopted from a file is written in place, leaving the rest of that file as it was.
- [ ] Where the working repository's local content
        — its own design documents, rules, or handbook —
        refers to process content the pull request renames,
        the same pull request updates those references so they keep resolving.
- [ ] Apart from those reference updates and any carrier for a human-applied unit,
        the pull request changes only process content the working repository has declared it
        adopts, and only the adopted parts of a file adopted in part;
        local content is otherwise byte-for-byte unchanged.
- [ ] Where applied process content carries a rule that the repository's existing local content
        does not follow — a heading-case rule against documents written before it, say —
        the skill reports which local content is affected and leaves it unchanged.

### Provenance

- [ ] Each pull request's description says what the change is,
        where it originated (the counterpart as the maintainer supplied it, its ref,
        and the upstream commits or pull requests), and why,
        quoting the source's own summary where one exists.
- [ ] Each pull request's title and description are specific enough that,
        once squash-merged, the resulting commit explains its lines to a reader of `git blame`.
- [ ] Each pull request is individually revertible through the repository's normal workflow.
- [ ] Applying the same proposal twice creates nothing the second time;
        the skill reports the pull requests that already exist and where.

### Nothing Crosses Unseen, Nothing Runs Unchosen

- [ ] The skill creates nothing the maintainer has not seen in that run:
        it shows what it is about to create, and creating it is the maintainer's explicit choice.
- [ ] When the working repository is public and a unit's content originates in a private repository,
        the skill shows the complete diff that would be pushed
        and creates no branch or pull request until the maintainer explicitly confirms
        that specific content is safe to publish;
        nothing the skill infers about the content substitutes for that confirmation.
- [ ] When the working repository is public and a unit's content originates in a private repository,
        the pull request names that repository, its ref, or its commits
        only if the maintainer chooses to include them;
        by default it says the change was synced from another repository that follows this process,
        and no more.
- [ ] The skill writes only to the working repository, and only as branches and pull requests;
        it does not approve, merge, or bypass branch protection.

### Documentation

- [ ] The skill's documentation covers applying a proposal:
        choosing units, combining them, the dry run,
        what the safe-to-publish confirmation looks like,
        and how to apply the counterpart's side.

## References

### Vision

- [One Development Process across Many Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement makes a proposal actionable while keeping every crossing between repositories
    behind a human in the receiving repository;
    it delivers the vision's "review once on the merits, mechanical review per repository" metric
    and its privacy and containment metrics for the on-demand case.

### Engineering Design

- [Process Sync Engineering Design](../engineering-designs/2026-10-13-process-sync.md) —
    Delivery as a deterministic tool with a dry run, the carrier for human-applied units,
    and the confirm stage.

### Analysis

- [Process Divergence across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
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
