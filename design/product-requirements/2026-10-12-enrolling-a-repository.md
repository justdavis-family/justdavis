---
title: Enroll a New Repository
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-09-06-process-sync-proposal
  - 2026-09-06-process-sync-apply
  - 2026-09-08-sync-decisions
  - 2026-10-04-unattended-sync-proposals
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-10-13-process-sync
prs: []
---

# Enroll a New Repository

## Summary

A repository that does not yet follow this `justdavis` monorepo's development process
  starts following it, and stays in sync from then on.
A repository that holds none of the process content yet does so through one pull request of its own.
A repository that already holds some of it — an earlier copy, or its own version of parts —
  enrolls through the same steps, and its existing content is reconciled as a sync would be,
  which may take as many pull requests as the grouping goals of
  [Propose a Process Sync](2026-09-06-process-sync-proposal.md) call for.
Either way, once enrolled, the new repository is a *working repository* like any other:
  it can produce and apply proposals, keep decisions, and run unattended,
  with the repository it adopted the process from as its *counterpart*.

Joining costs the repositories already following the process nothing.
None of them needs a change for a new one to join,
  and a private repository can join without any public repository learning that it has.
That is what keeps "two now, more later" from becoming a reason not to add a third.

## User Story

As a maintainer adopting this process in a new repository,
  I want to bring it to the current process and into ongoing sync with as little ceremony as a sync,
  so that it participates equally from then on
  and nothing about adding it falls on the repositories already there.

## Acceptance Criteria

### Joining

- [ ] The steps for enrolling a repository are documented as process content,
        so that they arrive with the process and stay current with it.
- [ ] A repository that holds none of the process content reaches the current process with one
        pull request of its own:
        the process content, its declaration of what it adopts and how its copies differ,
        and unattended sync turned on.
- [ ] A repository that already holds some of the process content enrolls through the same steps,
        and its existing content is reconciled as a sync:
        a proposal is produced against the counterpart and applied per
        [Apply a Process Sync Proposal](2026-09-06-process-sync-apply.md),
        with every human decision recorded per [Remember Sync Decisions](2026-09-08-sync-decisions.md),
        in as many pull requests as the proposal's grouping goals call for.
- [ ] After enrollment, a comparison between the new repository and its counterpart reports them
        in sync, apart from declared divergences and recorded decisions.
- [ ] Process content that assumes something untrue of the new repository
        — that it is a monorepo, say —
        is either generalized in the process or declared a divergence, as a recorded decision,
        rather than edited locally and left to drift.

### Equal Participation

- [ ] After enrollment, every requirement under the vision applies to the new repository
        as a working repository, with the repository it adopted the process from as its counterpart.
- [ ] After enrollment, an improvement made in the new repository can reach every other repository
        that follows the process, by way of the one they all follow;
        no repository that follows the process needs to be a counterpart to another.
- [ ] No repository already following the process needs any change for a new one to join.

### Privacy and Containment

- [ ] Enrolling a private repository adds nothing to any public repository:
        no content, no history, no registration, and nothing that identifies it.
- [ ] A private repository can enroll by following a public one,
        and needs no credential to do so beyond what reading a public repository requires.
- [ ] Enrollment does not require the new repository to hold any credential that would allow an
        attacker who acquires it to automatically compromise another repository.

### Documentation

- [ ] The process documentation covers enrollment end to end:
        the prerequisites, including any repository setting unattended sync needs that no pull
        request can turn on; the enrolling pull request or sync; declaring its divergences;
        and how to confirm the new repository is in sync afterwards.

## References

### Vision

- [One Development Process across Many Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement delivers the "cheap to join" metric,
    and keeps the "private stays private" metrics at the moment a private repository joins.

### Engineering Design

- [Process Sync Engineering Design](../engineering-designs/2026-10-13-process-sync.md) —
    The enroll tool and the one-sync enrollment it leads to.

### Analysis

- [Process Divergence across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
    What the first adoption cost when it was done by hand, and why the second should not.

### Engineering Principles

- [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md) —
    A new repository joins by reading, and holds nothing that reaches another repository.
- [YAGNI](../engineering-principles/2026-01-06-yagni.md) —
    Enrollment is a documented recipe and a sync, not a registry or an onboarding service.

### Related Requirements

- [Propose a Process Sync](2026-09-06-process-sync-proposal.md) —
    Confirms the new repository is in sync afterwards; this requirement depends on it.
- [Apply a Process Sync Proposal](2026-09-06-process-sync-apply.md) —
    Governs how existing content at process paths is treated; this requirement depends on it.
- [Remember Sync Decisions](2026-09-08-sync-decisions.md) —
    Records the decisions enrollment produces; this requirement depends on it.
- [Unattended Sync Proposals](2026-10-04-unattended-sync-proposals.md) —
    Turned on by the enrolling pull request; this requirement depends on it.

### Implementation

- None yet.
