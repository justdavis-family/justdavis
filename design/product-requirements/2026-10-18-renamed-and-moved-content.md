---
title: Renamed and Moved Shared Content
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-10-18-declared-divergences
extends:
  - 2026-10-18-declared-divergences
modifies: []
replaces: []
engineering_designs:
  - 2026-10-13-lockstep.md
prs: []
---

# Renamed and Moved Shared Content

## Summary

The [agent-assisted sync](2026-10-18-agent-assisted-sync.md) handles a rename by judgment:
  the agent notices the same content at a different path and lands a rename.
The [exact comparison](2026-10-18-exact-comparison.md) compares by path,
  so it reports a renamed file as missing on one side and unaccounted for on the other,
  and content moved between files as two unrelated edits.
This requirement lets the declaration map a path on one side to a path on the other,
  and recognizes renames and moves from history,
  so that the tools compare them as one thing and land them as renames.

This is the step most likely never to be needed.
If renames stay rare and the agent's handling of them proves adequate,
  the ladder stops before this requirement, and it stays a draft.

## User Story

As the maintainer of either repository,
  I want shared content that lives at different paths in the two repositories,
  or that has moved between files, compared as one thing and landed as a rename,
  so that history follows the file and a rename is never reported as a deletion and an addition.

## Acceptance Criteria

### Mapped Paths

- [ ] The declaration can map a shared path in one repository to a different path in the other.
- [ ] The comparison follows the mapping and reports the pair as one entry.
- [ ] Delivery writes to the mapped path.

### Renames and Moves since the Last Sync

- [ ] A shared file renamed in one repository since the last sync is recognized from history,
        and proposed here as a rename, or as a mapping, as the maintainer chooses.
- [ ] Content moved between shared files is recognized from history,
        and both halves of the move are kept in one pull request.
- [ ] Local references to renamed shared content are updated in the same pull request by the tools,
        not by the agent's attention.

### Documentation

- [ ] `.lockstep/README.md` covers mapped paths and how a rename is proposed and landed.

## References

### Vision

- [Shared Content in Lockstep across Two Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    After a sync, every reference from shared content resolves in the repository it landed in.

### Engineering Design

- [Lockstep Engineering Design](../engineering-designs/2026-10-13-lockstep.md) —
    How a change crosses, and which decisions are deliberately left undecided until needed.

### Analysis

- [Process Divergence across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
    The renamed-and-edited principles and the two cross-file moves that motivate this requirement.

### Related Requirements

- [Declared Divergences and Shared Parts of Files](2026-10-18-declared-divergences.md) —
    This requirement extends it, adding path mappings to the declaration.

### Implementation

- None yet.
