# Shared Content in Lockstep across Two Repositories

## Problem and Motivation

Some content belongs to more than one repository.
Two repositories with a shared lineage and a shared purpose end up holding the same agent
  instructions, the same shape of build and hook configuration, the same CI workflows,
  and the same design process, because the second was set up from the first and both need the
  same things.
Nothing keeps those copies aligned except someone remembering that the other repository exists
  and carrying the change over by hand,
  across a densely self-linked set of files that one improvement can touch fifteen or twenty of
  at once.
Copying is expensive, so drift is the default.
Once two copies have diverged, the next sync is a merge rather than a copy,
  which is more expensive still, so it is deferred longer.

The first instance is Karl's two monorepos: `justdavis`, which is public, and `justdavis-private`.
The private one adopted the public one's infrastructure by hand in April 2026, in one direction,
  and the two have diverged since.
As the [divergence inventory](../analyses/2026-09-04-process-divergence-inventory.md) records,
  `justdavis` has merged six process-only pull requests that never reached `justdavis-private`,
  and `justdavis-private` has made corrections to content that originated in `justdavis`
  — a spelling fix, a stale term in a review prompt, a missing engineering principle —
  that never came back.
A fix that was already found is found again, or never made,
  and an agent starting work in one repository follows an older process than the other.

## Vision

Lockstep keeps the content two repositories share moving in lockstep.
A change to shared content merged in either repository is as easy to make in the other as if it
  had been made there first:
  it arrives as a similar pull request, reviewed and merged through that repository's own workflow,
  with its origin and reasoning intact.

The first use case is infrastructure.
The agent instructions, the broad strokes of the `mise` build and the git hooks,
  the CI infrastructure, the design process, and sundry related items in `justdavis` and
  `justdavis-private` should stay in sync,
  so that an addition, a refinement, or a fix made in one is as easy as pie to make in the other.
Nothing about the approach is particular to infrastructure, though;
  any content two repositories share by lineage and by purpose is a candidate.

Each repository knows what it shares and where it is allowed to differ.
The shared set is explicit and discoverable from within either repository,
  and so are the places where a repository's copy intentionally departs from the other's.
Everything else is the repository's own:
  its projects, their design documents, its local rules and settings.
Local content is never touched by a sync, and local additions are first-class:
  a repository may add rules, principles, skills, and tasks beside the shared ones
  without them being removed or carried across.

Rules apply on arrival, but the debt lands locally.
When a heading-capitalization rule reaches a repository,
  that repository's existing documents do not become compliant by magic;
  bringing them into line is that repository's own follow-up work, tracked as such.
A sync promises that the rule is there, not that the past has been rewritten.

A human runs every sync and reviews every pull request it produces.
The work Lockstep removes is the finding, the copying, and the explaining, not the deciding.

### What This Is Not

- It is not a way to sync project content.
  Visions, requirements, designs, plans, and code about a repository's own projects stay where
    they are.
- It is not an attempt to make the two repositories identical.
  They differ by design outside the shared set, and inside it wherever a difference is declared.
- It is not a change to who decides what lands in a repository.
  Each repository keeps its own review and merge authority over its own content.
- It is not unattended automation.
  Nothing runs on a schedule, and nothing is created that a maintainer has not seen.

## Success Metrics

### In Lockstep

- A change to shared content merged in either repository reaches the other as a pull request
    for a few minutes of the maintainer's effort, in either direction.
- The same change is authored and reviewed on its merits once.
  Review in the receiving repository is mechanical
    — does it apply cleanly, do the references resolve —
    not a second review of the content.
- Whether the two repositories are in sync, and where they are not,
    can be told from either one without going looking.

### Nothing Broken, Nothing Lost

- After a sync, every reference from shared content — links, imports, pointers — resolves in the
    repository it landed in, and every declared difference keeps that repository's own value.
- A repository's local content is byte-for-byte untouched by a sync.
- When the same shared content is changed in both repositories before either change has reached
    the other, both changes are surfaced together; neither is silently overwritten.

### Public Stays Safe

- A pull request opened against `justdavis` is a publication, not a review step.
  Nothing authored in `justdavis-private` is pushed there until the maintainer has seen that exact
    content and confirmed it is safe to publish.
  An agent's judgment that a change is "only infrastructure" is never a substitute for that
    confirmation, however plausible the judgment.

## Requirements

This vision is being implemented through the following requirements, each building on the one before:

- [Agent-Assisted Sync of Shared Content](../product-requirements/2026-10-18-agent-assisted-sync.md) —
    A skill, run in either repository and pointed at a checkout of the other,
    that carries the other's changes to shared content here as pull requests,
    with the maintainer seeing everything before it is created (draft).
- [Exact Comparison of Shared Content](../product-requirements/2026-10-18-exact-comparison.md) —
    One command, needing no agent, that reports exactly which shared paths differ and how (draft).
- [Exact Delivery of a Sync](../product-requirements/2026-10-18-exact-delivery.md) —
    What the maintainer approved in a dry run is byte-for-byte what lands,
    with the publication confirmation enforced by a tool (draft).
- [Declared Divergences and Shared Parts of Files](../product-requirements/2026-10-18-declared-divergences.md) —
    Intentional differences, declines, and partially shared files honored deterministically
    rather than re-judged on each run (draft).
- [Renamed and Moved Shared Content](../product-requirements/2026-10-18-renamed-and-moved-content.md) —
    Content shared at different paths, or moved between files,
    compared as one thing and landed as a rename (draft).
