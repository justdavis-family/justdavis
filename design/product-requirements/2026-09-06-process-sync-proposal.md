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
        then classifies each difference using both repositories' histories as:
        an edit; an addition; a removal; a rename (same content, different name);
        a rename plus an edit; or content moved between files.
      Differences that only make sense together — the two halves of a content move,
        the files touched by one upstream change — are grouped as one item.
- [ ] The proposal lists, for each repository, the pull requests that would converge it:
        the files each would touch, the direction the content flows, a rationale,
        and the provenance (the commits or pull requests where the change originated).
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
