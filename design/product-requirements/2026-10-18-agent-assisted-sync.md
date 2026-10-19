---
title: Agent-Assisted Sync of Shared Content
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on: []
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-10-13-lockstep.md
prs: []
---

# Agent-Assisted Sync of Shared Content

## Summary

A Claude Code skill that a maintainer runs inside one repository — the *working repository* —
  pointed at a checkout of the other,
  to carry the other repository's changes to their shared content here as pull requests.
The skill reads the two repositories' declaration of what they share, finds what differs,
  reads both histories to learn where each difference came from,
  and opens one pull request here per upstream change,
  titled and described as if the change had been made here first.
It leans on judgment throughout:
  the agent decides what counts as the same change, how a renamed or partly shared file should land,
  and what to say about it, and the maintainer reviews every pull request before it merges.

This is deliberately the whole use case in one step.
Later requirements add deterministic tools where real use shows the agent to be slow, costly,
  or unreliable; this one establishes what real use looks like.

The two repositories today are `justdavis` and `justdavis-private`,
  and their shared content is their infrastructure:
  the agent instructions, the design process and its skill, the engineering principles,
  the `.github/` templates and workflows,
  and the broad strokes of the `mise` build and the git hooks.

## User Story

As the maintainer of either repository,
  I want to point a skill at a checkout of the other
  and have its changes to our shared content arrive here as pull requests I can review and merge,
  so that keeping the two in lockstep is a review task
  rather than a hand-copy across a self-linked set of files.

## Acceptance Criteria

### What Is Shared

- [ ] Both repositories hold a short, human-readable declaration of what they share, by path,
        and it is itself shared content, so that the two agree on what the shared set is.
- [ ] The declaration can note that a path is shared only in part,
        or that a repository's copy intentionally differs,
        in plain words for the agent and the maintainer to honor;
        nothing more structured is required of it here.
- [ ] Local additions — a repository's own rules, principles, skills, and tasks —
        need no mention in the declaration.

### What the Skill Produces

- [ ] For each change to shared content that the other repository has and this one lacks,
        the skill opens a branch and a pull request here,
        following this repository's conventions for branch names, titles, descriptions, and labels.
- [ ] By default each upstream pull request becomes one pull request here;
        the skill may combine or split them when it says why,
        and never separates the two halves of a rename or of content moved between files.
- [ ] Each pull request's description says what the change is and why,
        quoting the upstream summary where one exists,
        and names the repository, ref, commits, and pull requests it came from.
- [ ] Renames land as renames,
        and local references to renamed shared content are updated in the same pull request.
- [ ] Where a declared partial share or intentional difference applies,
        the repository's own content is left in place;
        where the skill cannot tell whether a difference is intentional, it asks rather than guesses.
- [ ] Where arriving content carries a rule that this repository's existing local content does not
        follow, the pull request reports which local content is affected and leaves it unchanged.
- [ ] Against two repositories whose shared content already matches,
        the skill creates nothing and says so.

### Nothing Crosses Unseen

- [ ] Before creating anything, the skill shows the maintainer every branch and pull request it is
        about to create, with its content; creating them is the maintainer's explicit choice.
- [ ] When the working repository is `justdavis` and the content comes from `justdavis-private`,
        the skill shows the complete diff that would be pushed
        and creates nothing until the maintainer confirms that specific content is safe to publish.
- [ ] The skill writes only to the working repository, and only as branches and pull requests;
        it never writes to the other repository,
        and never approves, merges, or bypasses branch protection.
- [ ] Run again after its pull requests exist, the skill reports them and creates nothing new.

### Proven on the Real Repositories

- [ ] The skill alone has brought `justdavis` and `justdavis-private` into sync, in both directions.
- [ ] The maintainer has recorded where the skill was slow, costly, or unreliable,
        so that the requirements that follow rest on evidence rather than on anticipation.

### Documentation

- [ ] `.lockstep/README.md`, itself shared content, explains what Lockstep is,
        what the skill does and never does, how to run it, and how to review what it opens.

## References

### Vision

- [Shared Content in Lockstep across Two Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement is the vision's whole use case in its first, judgment-based form.

### Engineering Design

- [Lockstep Engineering Design](../engineering-designs/2026-10-13-lockstep.md) —
    The decision to start from judgment and add determinism where it earns its place,
    and where the declaration and the skill live.

### Analysis

- [Process Divergence across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
    The divergence this skill first has to close, and the human decisions closing it requires.

### Related Requirements

- [Exact Comparison of Shared Content](2026-10-18-exact-comparison.md) extends this requirement.

### Implementation

- None yet.
