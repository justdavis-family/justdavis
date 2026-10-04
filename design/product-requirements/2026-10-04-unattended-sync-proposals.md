---
title: Unattended Sync Proposals
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-09-06-process-sync-proposal
  - 2026-09-06-process-sync-apply
  - 2026-09-08-sync-decisions
extends: []
modifies: []
replaces: []
engineering_designs: []
prs: []
---

# Unattended Sync Proposals

## Summary

[Propose a Process Sync](2026-09-06-process-sync-proposal.md) and
  [Apply a Process Sync Proposal](2026-09-06-process-sync-apply.md)
  keep this `justdavis` monorepo's development process in sync with the repositories that follow it,
  but only when a maintainer remembers to run them.
This requirement removes the remembering.
A repository that follows the process — the *working repository* —
  compares itself against a *counterpart repository* on its own, without a maintainer present,
  and puts what it finds in front of the maintainer as things to review.

What it finds takes two forms, by direction.
Changes that should come *in* from the counterpart arrive as open pull requests
  in the working repository.
Changes that should go *out* to the counterpart arrive as approval requests
  in the working repository, each carrying the complete diff and the proposed pull-request
  description, so that a human can decide whether that exact content may leave.
Nothing is sent to the counterpart by this requirement,
  and nothing that arrives from the counterpart runs until a human has chosen to run it.

Everything happens in the working repository.
The counterpart is only read, so it needs to run nothing, hold nothing, and know nothing
  about the repositories that follow it
  — which is what lets a private repository follow a public one
  without the public one ever learning that it exists.

## User Story

As a maintainer of a repository that follows this process,
  I want the repository to notice on its own when it and its counterpart have diverged
  and to put the resulting changes in front of me for review,
  so that staying in sync does not depend on my remembering to check,
  and nothing crosses between repositories or runs without my say.

## Acceptance Criteria

### Running Unattended

- [ ] The working repository compares itself against its counterpart on a recurring basis,
        without a maintainer present, and a maintainer can also trigger a run on demand.
- [ ] A process change merged in the counterpart is put in front of the working repository's
        maintainer within the bounded time the vision sets.
- [ ] When the two repositories' process content matches,
        apart from declared variations and recorded decisions, a run creates nothing.
- [ ] A run that could not compare the repositories, or could not produce a proposal,
        reports that to the maintainer as a failure;
        it is never indistinguishable from the repositories being in sync.

### Inbound Changes

- [ ] Each unit the proposal addresses to the working repository arrives there as an open pull request,
        with the content and provenance that Apply a Process Sync Proposal requires.
- [ ] Nothing in such a pull request — a workflow, a build, a test —
        executes in the working repository until a human has reviewed it and chosen to run it.
- [ ] A unit that depends on a decision only a human can make is not opened;
        the decision is put to the maintainer instead, with no default applied.
- [ ] Units the proposal marks as human-applied only are reported to the maintainer and not applied.

### Outbound Changes

- [ ] Each unit the proposal addresses to the counterpart arrives in the working repository as an
        approval request, carrying the complete diff and the proposed pull-request title and
        description.
- [ ] An approval request records a human's explicit approval or refusal of that exact content.
- [ ] Nothing is sent to, or created in, the counterpart by this requirement,
        whether or not a request has been approved.

### Not Repeating Itself

- [ ] A later run updates the pull requests and approval requests an earlier run created,
        rather than creating duplicates.
- [ ] A pull request or approval request that no longer applies
        — the repositories have since converged on that content — is closed, saying why.
- [ ] A unit the maintainer declines is recorded per
        [Remember Sync Decisions](2026-09-08-sync-decisions.md) and is not put forward again.

### Privacy and Containment

- [ ] The counterpart is not required to run anything, hold any credential,
        or record anything about the working repository.
- [ ] This requirement can be met in full by a private working repository following a public
        counterpart; a public repository is never required to run it against a private one.
- [ ] Reading a public counterpart requires no credential.
- [ ] The working repository is not required to hold any credential that would allow an attacker
        who acquires it to automatically compromise another repository.

### Documentation

- [ ] The process documentation covers how a repository turns this on, what it will create,
        and how a maintainer responds to an inbound pull request, an approval request,
        and a reported failure.

## References

### Vision

- [One Development Process Across Many Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement delivers the vision's "staleness is visible without anyone going looking for it"
    and bounded-time metrics, while keeping its "private stays private" and
    "compromise stays contained" metrics: everything is driven from the repository that follows,
    and nothing forwarded executes unreviewed.

### Engineering Design

- None yet.

### Analysis

- [Process Divergence Across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
    What going unnoticed costs: five months of divergence, in both directions,
    because checking depended on someone remembering to.

### Engineering Principles

- [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md) —
    The counterpart is only read, and the working repository writes only to itself.
- [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md) —
    A run that fails says so; silence means "in sync" and nothing else.

### Related Requirements

- [Propose a Process Sync](2026-09-06-process-sync-proposal.md) —
    Produces the proposal each run works from; this requirement depends on it.
- [Apply a Process Sync Proposal](2026-09-06-process-sync-apply.md) —
    Defines what an inbound pull request contains; this requirement depends on it.
- [Remember Sync Decisions](2026-09-08-sync-decisions.md) —
    Keeps declined units from being put forward again; this requirement depends on it.

### Implementation

- None yet.
