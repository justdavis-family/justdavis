---
title: Propose a Process Sync
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on: []
extends: []
modifies: []
replaces: []
engineering_designs: []
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

The skill reads a manifest that says which files are process content, which of those may vary per
  repository and how, and which files are local by design;
  compares the process content of the two repositories, honouring the declared variations;
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
The manifest describes the process content wherever it lives:
  if a later design moves some of it into a shared skill or plugin,
  the manifest lists the in-repository stubs and the installed version instead of the files,
  and the comparison compares those.

## User Story

As a maintainer working in one repository that follows this process,
  I want to point a skill at another repository that follows it
  and receive a proposal of the pull requests that would bring both to one current process,
  so that I can see exactly how they have diverged and decide what to do
  before anything in either repository changes.

## Acceptance Criteria

### The Boundary Manifest

The manifest is the skill's definition of what "process content" means,
  and is itself process content, held in every repository that follows the process.

- [ ] Every element of the development process is listed in the manifest by path;
        nothing is process content by implication.
- [ ] Every entry is classified as one of: shared verbatim; shared with a declared variation point;
        or local by design.
- [ ] Local-by-design entries exist only for files a reader would otherwise assume are shared:
        the contributor handbook, the repository-wide agent brief, agent settings,
        CI configuration, and the tool configuration at the root.
- [ ] Each variation point names what may differ
        (for example, the example pull-request URL in the requirements template),
        and the per-repository value is held in a local file the manifest points at,
        never inside the shared file.
- [ ] Adding a repository-local rule, principle, or skill requires no change to the manifest.
- [ ] The comparison reports a manifest entry whose path does not exist,
        or whose variation point has no local value, as an error rather than skipping it.

### Comparison and Reference Checks That Need No Agent

Two commands underlie the skill and can be run on their own,
  so that later requirements can run them unattended.

- [ ] The comparison takes the working repository at one ref and the counterpart at another,
        and reports, per manifest entry, exactly one of:
        identical, differs, missing in the working repository, missing in the counterpart.
- [ ] Declared variations are substituted before comparison, so a declared difference is not reported.
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
Units are chosen to minimise the net review burden across all of them
  — the fixed cost of every additional pull request weighed against the load of unrelated changes
  sharing one —
  and to leave a history in which each commit's summary explains the lines it touched.
Mirroring the upstream pull requests usually serves both readers;
  a long backlog may call for regrouping by topic.
How to weigh those goals in a given case is a judgement:
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
        whether a file present on one side only is adopted or declared local —
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
- [ ] The proposal identifies the counterpart only by the path the maintainer supplied,
        so that a proposal produced in a public repository carries no private repository's name or URL.

### Documentation

- [ ] The skill is documented alongside the design-process skill:
        what it does, what it never does, how to run it, and how to read a proposal.

## References

### Vision

- [One Development Process Across Many Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    This requirement makes divergence visible and explainable on demand,
    without changing or automating anything;
    every other requirement under the vision builds on the manifest, the checks, and the proposal
    it defines.

### Engineering Design

- None yet.

### Analysis

- [Process Divergence Across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md) —
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
