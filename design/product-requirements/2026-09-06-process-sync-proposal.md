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
  reads both repositories' histories to say *why* each difference exists
  (an edit, an addition, a removal, a rename, a rename plus an edit, or content moved between files);
  and writes a proposal: for each repository, the pull requests that would converge it,
  with rationale and provenance, and the decisions only a human can make.
It changes nothing in either repository.

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

- [ ] A manifest, held as process content in every repository that follows this process,
        lists every element of the development process by path;
        nothing is process content by implication.
- [ ] Every entry is classified as one of: shared verbatim; shared with a declared variation point;
        or local by design.
      Local-by-design entries exist only for files a reader would otherwise assume are shared
        (the contributor handbook, the repository-wide agent brief, agent settings, CI configuration,
        and the tool configuration at the root).
- [ ] Each variation point names what may differ (for example, the example pull-request URL in the
        requirements template) and the per-repository value is held in a local file
        that the manifest points at, never inside the shared file.
- [ ] Adding a repository-local rule, principle, or skill requires no change to the manifest.
- [ ] A manifest entry whose path does not exist, or whose variation point has no local value,
        is reported as an error by the comparison rather than silently skipped.

### Comparison and Reference Checks That Need No Agent

- [ ] A command compares the working repository's process content, at a given ref,
        against the counterpart repository's at a given ref,
        and reports, per manifest entry, exactly one of:
        identical, differs, missing in the working repository, missing in the counterpart.
      Variation points are substituted before comparison, so a declared difference is not reported,
        and a failure to compare is reported as a failure, never as "identical".
- [ ] A command checks that every reference from process content — Markdown links, `@`-imports,
        and skill pointers — resolves in the repository it is run in, and reports each that does not.
- [ ] Both commands run without an agent and signal findings in a way that unattended automation
        can act on.
- [ ] Comparing a public counterpart requires no credential.

### Which Revisions Are Compared

- [ ] Each side of a comparison is a specific ref, resolved to a commit and recorded in the output:
        by default the checked-out revision in the working repository
        and the default branch in the counterpart,
        with either overridable so that a maintainer can compare against a branch under review
        or an older release.
- [ ] Both sides are read as committed content; uncommitted changes in either working tree are
        reported as present and excluded from the comparison, never silently included.
- [ ] Because the working repository is usually on a branch under development
        and the counterpart's default branch is usually what the eventual pull requests target,
        the proposal states which ref each proposed pull request would be opened against.

### The Proposal

- [ ] Given the path to the counterpart repository's checkout, the skill runs the checks above,
        then uses both repositories' histories to explain and attribute each difference:
        which upstream commits or pull requests produced it,
        and whether it is an edit, an addition, a removal, a rename (same content, different name),
        a rename plus an edit, or content moved between files.
- [ ] The proposal groups differences into units, each of which becomes one proposed pull request,
        so as to minimise the *net* review burden across all of them:
        the fixed overhead of every additional pull request on one side,
        the mental load of unrelated changes sharing a pull request on the other.
- [ ] In the ordinary case — the repositories have followed each other closely,
        and the differences come from a small number of tightly scoped, non-overlapping upstream
        pull requests — each unit mirrors one upstream pull request.
- [ ] Where upstream pull requests overlap, because several rewrote the same content in turn,
        their net effect is one unit whose provenance names all of them;
        nothing intermediate is replayed.
      Units may also be combined where many small ones would cost more in overhead than they save.
- [ ] An upstream pull request is never split across units.
      Where a difference cannot be attributed to an upstream pull request at all,
        its unit is at least whatever leaves the working repository consistent:
        the two halves of a rename or of a content move stay together.
- [ ] The proposal lists, for each repository, the pull requests that would converge it:
        the files each would touch, the direction the content flows, a rationale,
        and the provenance (the upstream commits or pull requests the unit mirrors or combines).
- [ ] The proposal names every decision it cannot make itself — which of two filenames wins,
        whether a file present on one side only should be adopted or declared local —
        and states what it recommends and why.
- [ ] The proposal marks any item that must be applied by a human rather than by automation,
        and says why, so that a later unattended step knows what to leave alone.
- [ ] Running the skill against two converged repositories yields an empty proposal.
- [ ] The skill changes no tracked file in either repository.
      The proposal is delivered as output the maintainer can save wherever they choose.

### Privacy

- [ ] Every proposed change whose content originates in a private repository and whose destination is
        a public one is marked as requiring a human's explicit safe-to-publish confirmation
        before it may be applied, regardless of how routine the content looks.
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
    The real divergence this skill must classify correctly:
    renamed-and-edited principles, content moved between files, and repository-specific lines.

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
