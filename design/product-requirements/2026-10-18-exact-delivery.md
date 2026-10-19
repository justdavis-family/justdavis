---
title: Exact Delivery of a Sync
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-10-18-exact-comparison
extends:
  - 2026-10-18-agent-assisted-sync
modifies: []
replaces: []
engineering_designs:
  - 2026-10-13-lockstep.md
prs: []
---

# Exact Delivery of a Sync

## Summary

In the [agent-assisted sync](2026-10-18-agent-assisted-sync.md) the agent itself creates the
  branches and pull requests, and the publication confirmation is a step in its instructions.
What lands is therefore whatever the agent did, which the maintainer checks after the fact,
  and the confirmation holds only as long as the agent follows its instructions.
This requirement separates deciding from doing.
The agent writes what it proposes into a directory, as one unit per pull request,
  and a tool turns those units into branches and pull requests, byte for byte,
  after a dry run the maintainer has read.
The publication confirmation and the reference check belong to the tool,
  which cannot be talked out of them.

## User Story

As the maintainer of either repository,
  I want what I approved in a dry run to be exactly what lands,
  with the publication confirmation enforced by something that cannot be argued with,
  so that I review a sync once and trust its delivery.

## Acceptance Criteria

### From Proposal to Pull Request

- [ ] The skill writes each proposed pull request as a unit in an output directory
        — its changes, title, description, base ref, and provenance — and creates nothing itself.
- [ ] A tool creates the branches and pull requests from those units;
        its dry run prints every branch and pull request it would create, with content,
        and creates nothing.
- [ ] The maintainer can deliver the whole proposal or a chosen subset of its units.
- [ ] If the working repository no longer matches a unit
        — its base ref has moved on, or its changes no longer apply —
        the tool stops before creating anything and says what changed.
- [ ] The tool writes only paths the declaration names as shared,
        plus updates to local references to shared content a unit renames;
        it refuses a unit naming any other path.
- [ ] Before a pull request is opened, every reference from the shared content it carries is
        checked to resolve in the working repository, and a dangling one is reported.

### The Confirmation Is the Tool's

- [ ] When the working repository is `justdavis` and a unit's content comes from
        `justdavis-private`, the tool shows the unit's complete diff and creates nothing for it until
        the maintainer confirms that content is safe to publish;
        nothing the agent wrote in the unit substitutes for that confirmation,
        and no option skips it.
- [ ] Run again after its pull requests exist, the tool reports them and creates nothing new;
        where a unit's content has changed since, it updates that pull request rather than opening
        another.

### Documentation

- [ ] `.lockstep/README.md` covers delivery: the output directory, the dry run,
        choosing units, what the confirmation looks like, and what the tool refuses.

## References

### Vision

- [Shared Content in Lockstep across Two Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    A pull request opened against `justdavis` is a publication, not a review step.

### Engineering Design

- [Lockstep Engineering Design](../engineering-designs/2026-10-13-lockstep.md) —
    The split between the agent and the tools, how a change crosses, and the publication check.

### Related Requirements

- [Agent-Assisted Sync of Shared Content](2026-10-18-agent-assisted-sync.md) —
    This requirement extends it, moving the creation of branches and pull requests from the agent
    to a tool.
- [Exact Comparison of Shared Content](2026-10-18-exact-comparison.md) —
    The report this requirement's units are drawn from.
- [Declared Divergences and Shared Parts of Files](2026-10-18-declared-divergences.md) extends
    this requirement.

### Implementation

- None yet.
