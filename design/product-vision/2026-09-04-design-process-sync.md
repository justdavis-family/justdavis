# One Development Process Across Many Repositories

## Problem and Motivation

This repository's development process — how work is designed, reviewed, tracked, and formatted —
  is not used only here.
One or more other repositories, some of which may be private, follow the same process:
  the same `design/` directory and templates, the same agent rules, the same review conventions.
The process is, in effect, a product.
Its users are the maintainers and agents of every repository that follows it,
  it changes through reviewed pull requests, and it has a skill, templates, rules, and workflows.

What it does not have is a way to reach its users.
Today an improvement made in one repository reaches another only if someone remembers the other
  repository exists, copies the change by hand, and does so across a densely self-linked set of files
  that a single process change can touch fifteen or twenty of at once.
That has happened once, in one direction, about five months ago.
Since then, as the [divergence inventory](../analyses/2026-09-04-process-divergence-inventory.md) records,
  this repository has merged six process-only pull requests that reached no other repository,
  and another repository has made corrections to this repository's own content
  — a spelling fix, a stale term in a review prompt, a missing engineering principle —
  that never came back.

The people and agents on the far end experience this directly.
An agent starting work in another repository follows an older process:
  no skill to route it, no pull-request template, different heading rules,
  a different convention for tracking delivery.
A human who learned the process in one repository finds it subtly different in the next,
  and review enforces different standards in each.
A fix that was already found is found again, or never made.
And the author of a process improvement faces a choice between a large manual copy and letting the
  repositories drift, which is no choice at all: drift is the default, because copying is expensive.

Drift then ratchets.
Once two repositories have diverged, the next sync is a merge rather than a copy,
  which is more expensive still, so it is deferred longer.
Every additional adopting repository multiplies the cost.
Meanwhile the value of process work is proportional to the number of repositories it governs;
  unsynced, every improvement pays off exactly once.

The root cause is not that copying is slow.
It is that the process has no single definition that every repository demonstrably follows.
It has several copies with no relationship between them.

## Vision

One development process, with one definition, maintained collectively by everyone who follows it.
Improve it from whichever repository you happen to be working in;
  within a short, bounded time every adopting repository follows the improved process,
  and nothing is broken on arrival.

A repository *follows the process* when the process content it uses is the current definition,
  except at points where a repository is explicitly allowed to differ.
Anything else is staleness, and staleness is visible rather than discovered by accident.

The boundary between process content and a repository's own content is explicit,
  discoverable from within any adopting repository, and part of the process itself.
Process content is the design directory's READMEs and templates, the design-process skill,
  the rules that govern process, the pull-request and issue templates, the process-related workflows,
  and the engineering principles.
Everything else is local: the design documents about a repository's own projects,
  its language and platform rules, its contributor handbook, its build and CI configuration,
  its tool and agent settings.
Local content is never touched by the process, and local *additions* are first-class:
  a repository may add rules, principles, and skills alongside the shared ones
  without them being removed or propagated.

Rules apply on arrival, but the debt lands locally.
When a heading-capitalisation rule reaches a repository,
  that repository's existing documents do not become compliant by magic;
  bringing them into line is that repository's own follow-up work, tracked as such.
The process promises that the rule is there, not that the past has been rewritten.

Contributors, human and agent, can find and read the current process from within any adopting
  repository.
Whether they read it in files that live in the repository, or by following a pointer to where the
  definition lives, is a design choice with real trade-offs on each side;
  this vision requires only that the reading is possible and that what they read is current.

Adopting a private repository never requires naming it in any public repository's content or history.
The public repository may be pointed at; it does not point back.

### What This Is Not

- It is not a way to sync project content.
  Visions, requirements, engineering designs, delivery plans, and analyses about a repository's own
    projects stay where they are.
- It is not an attempt to make repositories identical outside the process.
  Contributor handbooks, agent briefs, settings, and CI differ by design and keep differing.
- It is not a change to who decides what lands in a repository.
  Each repository keeps its own review and merge authority over its own content;
    whether a process change arrives as something to review or as something already applied
    is left to the requirements and the engineering design.
- It is not a per-repository veto on the process.
  Disagreement with a change is expressed by changing the process, which reaches everyone,
    or by declaring a point of allowed variation — not by quietly keeping an older copy.
- It is not a choice of mechanism.
  Shared skills, replication workflows, template repositories, subtrees, and hybrids of these
    are evaluated in an analysis, on their merits, against the metrics below.

## Success Metrics

### One Process

- At steady state, every adopting repository follows the current process,
    and whenever one does not, that fact is visible without anyone going looking for it.
- A process change merged in any adopting repository is followed by every other adopting repository
    within a bounded time — no more than a week, or before the next process change is authored,
    whichever comes first.
- Improvements flow in both directions with equal effort:
    a change authored in a private repository reaches the public one as readily as the reverse.
- The same shared change is authored and reviewed on its merits once.
  Whatever per-repository review the design requires is mechanical
    — does it apply cleanly, do the references resolve — not a second review of the content.

### Nothing Broken, Nothing Lost

- After any process change reaches a repository, every reference from process content
    — links, imports, pointers — resolves in the place it is consumed,
    and every point of allowed variation carries that repository's own value.
- A repository's local content is byte-for-byte untouched by process changes.
- When the same part of the process is changed in two repositories before either change has reached
    the other, both changes are surfaced together; neither is silently overwritten.

### Cheap to Join, Easy to Understand

- A new repository starts following the current process with one pull request of its own,
    and participates equally from then on.
- From any adopting repository alone, a contributor can tell which content is process
    and which is local, before editing either.

The concrete shape of these — how the boundary is declared, how staleness is detected,
  how a change travels, how conflicts are presented —
  is specified in the requirements and the engineering design, not here.

## Requirements

This vision is being implemented through the following requirements:

- [Process and Local Content Boundary](../product-requirements/2026-09-04-process-content-boundary.md) —
    An explicit, discoverable statement of what is process content, what may vary, and what is local
    (draft).
- [Staleness Is Visible](../product-requirements/2026-09-04-process-staleness-visibility.md) —
    Automatic notice when any adopting repository is not following the current process (draft).
- [Process Content Integrity in Each Repository](../product-requirements/2026-09-04-process-content-integrity.md) —
    Every reference from process content resolves where it is consumed (draft).
- [Initial Convergence of the Existing Repositories](../product-requirements/2026-09-04-initial-process-convergence.md) —
    The repositories that already follow the process are brought to one current definition (draft).
- [A Process Change Made Once Reaches Every Repository](../product-requirements/2026-09-04-process-change-propagation.md) —
    A change merged anywhere is followed everywhere, as one unit, within the bounded time (draft).
- [Concurrent-Change Conflict Resolution](../product-requirements/2026-09-04-process-change-conflicts.md) —
    Competing changes are detected and resolved into one definition (draft).
- [Enrolling an Additional Repository](../product-requirements/2026-09-04-enrolling-a-repository.md) —
    A new repository joins with one pull request (draft).
