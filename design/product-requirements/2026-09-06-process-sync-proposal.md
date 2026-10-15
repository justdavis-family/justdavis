---
title: Propose a Process Sync
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on: []
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-10-13-process-sync.md
prs: []
---

# Propose a Process Sync

## Summary

An agent skill that a maintainer runs inside one repository — the *working repository* —
  pointed at a checkout of another — the *counterpart repository* —
  to find out how the two repositories' development-process content has diverged
  and what it would take to bring them to one current process.
The development process in question is the one this `justdavis` monorepo defines
  — its `design/` directory and the document types, templates, and sequence described in
  [`design/README.md`](../README.md); the design-process skill; the agent rules that govern process;
  the pull-request and issue templates; the process-related workflows; and the engineering principles —
  as followed by this repository and by the other repositories that adopted it from here.
The skill is not a general tool for comparing arbitrary repositories.

The skill reads the working repository's declaration of which process content it adopts from the
  counterpart — whole files, or named parts of files whose remainder is the repository's own —
  and how its copies are allowed to differ;
  compares that content between the two repositories, honoring the declared divergences;
  reads both repositories' histories to say where each difference came from and what kind of change
  it is;
  and writes a proposal: for each repository, the pull requests that would converge it,
  with rationale and provenance, and the decisions only a human can make.
It changes nothing in either repository.

The proposal is shaped for two readers at once.
The first is the reviewer of each proposed pull request,
  whose net burden across all of them should be as low as possible.
The second is whoever later reads the repository's history,
  for whom each commit's summary should explain the lines it touched
  rather than saying something as vague as "adopt the current process".
Mirroring the upstream pull requests usually serves both;
  when a backlog has accumulated, regrouping some changes may serve them better.

The comparison and a reference-integrity check can run on their own, without an agent,
  so that a later requirement can run them unattended;
  the skill adds the history-based explanation and the proposal on top.
The declaration describes the process content wherever it lives:
  if a later design ever moved some of it into a shared skill or plugin
  — which the [mechanisms analysis](../analyses/2026-10-12-cross-repo-process-sync.md)
  decides against —
  the declaration would list the in-repository stubs and the installed version instead of the files,
  and the comparison would compare those.

## User Story

As a maintainer working in one repository that follows this process,
  I want to point a skill at another repository that follows it
  and receive a proposal of the pull requests that would bring both to one current process,
  so that I can see exactly how they have diverged and decide what to do
  before anything in either repository changes.

## Acceptance Criteria

### What Is Adopted, and Where It Differs

Each repository that follows the process declares what it adopts from its counterpart.
The declaration is the skill's definition of what "process content" means in that repository.
It is the repository's own content, held in the repository it describes and never itself synced.

- [ ] Every piece of process content a repository adopts is declared by path;
        nothing is process content by implication.
- [ ] A declaration can adopt a whole file,
        or named parts of a file whose remainder is the repository's own,
        so that a file mixing general and repository-specific content
        — the repository-wide agent brief, a conventions rule each repository extends —
        can be kept in sync without surrendering the rest.
- [ ] A declaration can state how the repository's copy differs from the counterpart's
        (for example, the issue it links for label automation),
        as a substitution or as a larger divergence,
        recorded in the declaration and never as a placeholder inside the content itself.
- [ ] The counterpart lists what it offers, and may suggest parts and substitutions;
        the proposal reports anything offered that the working repository neither adopts nor
        declines, so that new process content is never silently missed.
- [ ] Files a reader would otherwise assume are shared
        — the contributor handbook, the repository-wide agent brief, agent settings,
        CI configuration, and the tool configuration at the root —
        are documented as each repository's own, or as adopted only in part,
        so that no reader assumes them shared.
- [ ] Adding a repository-local rule, principle, or skill requires no change to the declaration.
- [ ] The comparison reports an adopted path that does not exist,
        a declared part it cannot locate exactly once,
        or a declared divergence that no longer applies,
        as an error rather than skipping it.

### Comparison and Reference Checks That Need No Agent

Two commands underlie the skill and can be run on their own,
  so that later requirements can run them unattended.

- [ ] The comparison takes the working repository at one ref and the counterpart at another,
        and reports, per declared entry, exactly one of:
        identical, differs, missing in the working repository, missing in the counterpart,
        or declined by the working repository;
        and reports separately what the counterpart offers that is neither adopted nor declined.
- [ ] Declared divergences are applied before comparison, so a declared difference is not reported;
        a part adopted from a file is compared on its own, and the rest of that file is not.
- [ ] A failure to compare an entry is reported as a failure, never as "identical".
- [ ] The reference check reports every reference from process content
        — Markdown links, `@`-imports, and skill pointers —
        that does not resolve in the repository it is run in.
- [ ] Both commands run without an agent and exit in a way that unattended automation can act on.
- [ ] Neither command needs a credential when the counterpart is public.

### Which Revisions Are Compared

- [ ] Each side of a comparison is a specific ref, resolved to a commit and recorded in the output.
- [ ] By default the working side is the checked-out revision and the counterpart side is its
        default branch; either can be overridden,
        so that a maintainer can compare against a branch under review or an older release.
- [ ] Uncommitted changes in either working tree are reported as present and excluded from the
        comparison, never silently included.
- [ ] The proposal states which ref each proposed pull request would be opened against,
        since the working repository is usually on a branch under development
        and the counterpart's default branch is usually the eventual target.

### Explaining Each Difference

- [ ] For each difference, the proposal names the upstream commits and/or pull requests that produced it,
        drawn from both repositories' histories.
- [ ] For each difference, the proposal says whether it is an edit, an addition, a removal,
        a rename (same content, different name), a rename plus an edit,
        or content moved between files.

### Grouping Differences into Pull Requests

Each unit in the proposal becomes one proposed pull request.
Units are chosen to minimize the net review burden across all of them
  — the fixed cost of every additional pull request weighed against the load of unrelated changes
  sharing one —
  and to leave a history in which each commit's summary explains the lines it touched.
Mirroring the upstream pull requests usually serves both readers;
  a long backlog may call for regrouping by topic.
How to weigh those goals in a given case is a judgment:
  the heuristics are recorded in the engineering design and are expected to evolve with use,
  and the maintainer can regroup before applying.

- [ ] No unit would leave the working repository inconsistent on its own:
        the two halves of a rename, or of a content move, are always in the same unit.
- [ ] Each unit names the upstream commits and/or pull requests it draws from.
- [ ] The proposal states how it grouped the differences and why,
        so that a maintainer can judge the grouping against the goals above and change it.

### The Proposal

- [ ] For each repository, the proposal lists the pull requests that would converge it:
        the files each touches, the direction the content flows, its rationale, and its provenance.
- [ ] The proposal names every decision it cannot make itself
        — which of two filenames wins,
        whether a file present on one side only is adopted or declined —
        with a recommendation and the reason for it.
- [ ] The proposal marks any item that must be applied by a human rather than by automation,
        and says why.
- [ ] Against two converged repositories, the proposal is empty.
- [ ] The skill changes no tracked file in either repository;
        the proposal is output the maintainer can save wherever they choose.

### Privacy

- [ ] Every proposed change whose content originates in a private repository and whose destination is
        a public one is marked as requiring a human's explicit safe-to-publish confirmation
        before it may be applied, however routine the content looks.
- [ ] The proposal identifies the counterpart only by the path or URL the maintainer supplied,
        so that a proposal produced in a public repository carries no private repository's name or URL.

### Documentation

- [ ] The skill is documented alongside the design-process skill:
        what it does, what it never does, how to run it, and how to read a proposal.

## References

### Vision

- [One Development Process across Many Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement makes divergence visible and explainable on demand,
    without changing or automating anything;
    every other requirement under the vision builds on the declaration, the checks, and the
    proposal it defines.

### Engineering Design

- [Process Sync Engineering Design](../engineering-designs/2026-10-13-process-sync.md) —
    The counterpart's catalog, the repository's manifest, the comparison, the reference check,
    the skill, and the proposal format.

### Analysis

- [Process Divergence across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
    The real divergence this skill must explain and group correctly:
    renamed-and-edited principles, content moved between files, repository-specific lines,
    and a five-month backlog of overlapping upstream pull requests.

### Engineering Principles

- [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md) —
    The skill writes nothing and needs no credential; comparing against a public repository
    needs no secret at all.
- [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md) —
    "Identical", "differs", and the two kinds of "missing" are distinct outcomes;
    a failure to compare is reported as a failure, never as "identical".

### Related Requirements

- None yet.

### Implementation

- None yet.
