---
title: Remember Sync Decisions
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-09-06-process-sync-proposal
  - 2026-09-06-process-sync-apply
extends: []
modifies: []
replaces: []
engineering_designs: []
prs: []
---

# Remember Sync Decisions

## Summary

Syncing two repositories produces decisions that neither repository's content records:
  a piece of process content this repository has chosen not to adopt;
  a conflict a human resolved one way rather than the other;
  the canonical name chosen for a file the two sides had named differently;
  a difference accepted as a permanent variation.
Nothing in either repository's history says any of that,
  so without a record every later proposal asks the same questions again,
  and a conflict resolved on one side is raised afresh on the other
  until the two happen to match.

This requirement gives each repository a log of the decisions made during its syncs,
  which proposals honor and cite.
A decision made once is not asked twice;
  a resolution made on one side is carried to the other rather than re-raised;
  and anyone wondering why the repositories differ where they do can find the answer.
Decisions are per repository, because "declined here" is not "declined everywhere",
  and the log lives in the repository whose decisions it records.

## User Story

As a maintainer who has already decided how a difference should be handled,
  I want that decision remembered and honored by every later proposal,
  so that I am never asked the same question twice
  and a resolution I made on one side is carried to the other rather than raised again.

## Acceptance Criteria

### What Is Remembered

- [ ] A repository that follows the process keeps a log of the decisions made during its syncs,
        each with what was decided, why, when, and by whom.
- [ ] The log can record at least: declining a piece of process content;
        resolving a conflict; choosing the canonical name for content the two sides named
        differently; and accepting a difference as a permanent variation.
- [ ] A decision is recorded in the same pull request that carries it out,
        so that the log never describes a decision the repository has not actually applied.
- [ ] The log is local content: it is never itself synced,
        and the manifest classifies it as local by design.

### How Decisions Are Honored

- [ ] A proposal does not ask a question the log already answers;
        where a decision applies, the proposal cites it instead.
- [ ] A declined piece of process content is not proposed again,
        and the comparison reports it as declined rather than as missing.
- [ ] A conflict resolved in one repository is carried to the other as the resolution,
        not raised there as a conflict a second time.
- [ ] A maintainer can revisit any decision;
        revisiting it is recorded as a new decision that supersedes the old one,
        and the old one stays in the log.

### Privacy

- [ ] A decision recorded in a public repository describes content and reasons,
        never a private counterpart:
        it does not name the repository the sync was with, its refs, or its commits.
- [ ] A private repository's log may name the public counterpart freely.

### Documentation

- [ ] The skill's documentation covers the log: what it records, where it lives,
        how a proposal cites it, and how to revisit a decision.

## References

### Vision

- [One Development Process Across Many Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement keeps the vision's "reviewed once on the merits" promise across time:
    a decision reviewed once stays made,
    and the "private stays private" metrics govern where it is written down.

### Engineering Design

- None yet.

### Analysis

- [Process Divergence Across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
    Its recommendation lists the decisions the initial convergence will produce:
    canonical principle names and dates, adopt-or-decline for side-only files,
    and generalize-or-vary for repository-specific lines.
  Those are the log's first entries.

### Engineering Principles

- [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md) —
    "Declined" is a distinct outcome from "missing", and the comparison reports it as such.

### Related Requirements

- [Propose a Process Sync](2026-09-06-process-sync-proposal.md) —
    Produces the proposals that honor and cite the log; this requirement depends on it.
- [Apply a Process Sync Proposal](2026-09-06-process-sync-apply.md) —
    Carries decisions out, and records them in the same pull request; this requirement depends on it.

### Implementation

- None yet.
