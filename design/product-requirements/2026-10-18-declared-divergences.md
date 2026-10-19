---
title: Declared Divergences and Shared Parts of Files
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-10-18-exact-delivery
extends:
  - 2026-10-18-exact-comparison
  - 2026-10-18-exact-delivery
modifies: []
replaces: []
engineering_designs:
  - 2026-10-13-lockstep.md
prs: []
---

# Declared Divergences and Shared Parts of Files

## Summary

In the [agent-assisted sync](2026-10-18-agent-assisted-sync.md),
  the places where the two copies intentionally differ are noted in plain words,
  and the agent honors them by judgment on every run.
The [exact comparison](2026-10-18-exact-comparison.md) compares whole paths,
  so it reports every such place as differing, and leaves the agent to explain it away each time.
This requirement makes intentional differences exact.
A repository can declare a substitution, its own value at a named point in a shared file;
  a decline, shared content it does not take, with a reason;
  and a shared part of a file whose remainder is its own.
The comparison applies the declarations before comparing and never reports a declared difference,
  and delivery writes a shared part in place.
Each such declaration is a decision, recorded once and honored from then on.

## User Story

As the maintainer of either repository,
  I want the places where our copies intentionally differ, the shared content one side declines,
  and the files only partly shared to be declared once and honored exactly,
  so that the comparison never reports a difference I have already decided on
  and the agent never re-judges it.

## Acceptance Criteria

### What Can Be Declared

- [ ] A repository can declare a substitution: its own value at a named point in a shared file,
        such as the issue it links for label automation,
        recorded in the declaration and never as a placeholder inside the content itself.
- [ ] A repository can decline shared content, with a reason.
- [ ] A repository can declare a part of a file as shared,
        so that a file mixing shared and local content
        — the repository-wide agent brief, a conventions rule each repository extends —
        can be kept in sync without surrendering the rest.
- [ ] Substitutions, declines, and the location of shared parts are the repository's own content
        and are never synced;
        what is shared stays in the shared declaration.
- [ ] A declared point that cannot be located exactly once in the file it applies to is an error,
        never a guess.

### How Declarations Are Honored

- [ ] Declarations are applied before comparison, so a declared difference is never reported.
- [ ] A declined path is reported as declined, never as missing.
- [ ] A decline made against one version of the content does not silently cover a changed later one:
        the comparison says when declined content has changed since the decline,
        so that the maintainer can renew or revisit it.
- [ ] A shared part of a file is compared on its own and the rest of the file is not;
        delivery writes a shared part in place and leaves the rest of the file as it was.
- [ ] A declaration is recorded in the same pull request that carries out the decision it records,
        so that the record never claims a decision the repository has not applied.
- [ ] When, why, and by whom each declaration was made can be read from the repository.

### Documentation

- [ ] `.lockstep/README.md` covers substitutions, declines, and shared parts:
        how to declare each, how the comparison reports them, and how to revisit one.

## References

### Vision

- [Shared Content in Lockstep across Two Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    Each repository knows what it shares and where it is allowed to differ.

### Engineering Design

- [Lockstep Engineering Design](../engineering-designs/2026-10-13-lockstep.md) —
    How mixed files are handled, how the shared set is declared, and where decisions live.

### Related Requirements

- [Exact Comparison of Shared Content](2026-10-18-exact-comparison.md) and
    [Exact Delivery of a Sync](2026-10-18-exact-delivery.md) —
    This requirement extends both, teaching the comparison and the delivery about declarations.
- [Renamed and Moved Shared Content](2026-10-18-renamed-and-moved-content.md) extends this
    requirement.

### Implementation

- None yet.
