# Delivery Plans

This directory contains delivery plans for projects in this monorepo.

## Purpose

Delivery plans capture *how* a product vision or set of requirements will be
  delivered iteratively — which PRs and milestones are planned, in what order,
  and what each one will contain.
They are distinct from engineering design documents (which capture *how* the system is built)
  and from product requirements (which capture *what* to build and its acceptance criteria).

The primary value of a delivery plan is **scope management**:
  forcing an explicit decision about what goes into which PR,
  before development begins, reduces over-commitment on first-cut scope
  and helps identify where requirements can be sliced more thinly.

A delivery plan is **not** a task list or an implementation recipe.
It does not specify the detailed steps inside each PR —
  that is left to the developer or agent doing the work.
It answers: "What are the milestones, and what does each one deliver?"

## When to Write a Delivery Plan

Write a delivery plan when:

- A product requirement or set of requirements feels large or risky.
- The first-cut scope is unclear or potentially over-committed.
- The work spans multiple PRs or phases and the sequencing matters.
- You want to surface delivery risk early, before getting stuck in a large PR
    or an endless review loop.

Simple, clearly-scoped requirements that fit comfortably in one PR do not need a delivery plan.

## What Makes a Good Delivery Plan

- **Thin slices**: each milestone or PR delivers something independently usable or testable,
    not just an intermediate state that only makes sense in hindsight.
- **Clear scope boundaries**: what is explicitly *in* each milestone, and what is deferred.
- **Honest deferral**: separate work that is *required for the feature to function* from
    *nice-to-have UX or polish*; sequence the latter into explicitly-optional later milestones
    (that may never be reached) or drop it entirely, rather than bundling it into the first cut.
- **Human decisions recorded**: the plan captures choices about sequencing and scope
    that aren't obvious from the requirements themselves.

## Tracking Delivery in GitHub Issues

Design documents and GitHub issues play different roles, and the split matters:

- **The documents are authoritative for content.**
  What a requirement means, and what each milestone contains, lives in the docs.
- **The issues are authoritative for status.**
  Whether something is in progress, blocked, or done lives in the issue tracker.

Issues therefore *summarize and link* their documents rather than restating them.
When the two disagree about content, the document wins and the issue should be corrected.

### The Issue Hierarchy

Three levels of tracking issue mirror the design documents,
  each carrying a label matching its document type:

| Issue | Title format | Label | Mirrors |
|---|---|---|---|
| Vision | `<Project> — product vision` | `vision` | A product vision document. |
| Requirement | `<Project> — product requirement` | `requirement` | A product requirement document. |
| Milestone | `<Project> M<N> — <milestone title>` | `milestone` | One milestone in a delivery plan. |

Milestone issues are created as **GitHub sub-issues of the requirement issue** they deliver,
  so the requirement issue shows delivery progress without duplicating the milestone list.

### What Each Issue Contains

A **requirement issue** links to its requirement document, summarizes it in a paragraph,
  links to the related vision issue, records priority,
  and points at the delivery plan and the milestone sub-issues that deliver it.

A **milestone issue** links to the delivery plan and names which milestone it tracks,
  then restates that milestone's `Scope` and `Deliverable` briefly,
  and turns the milestone's scope into an **acceptance-criteria checklist** that can be ticked off.
Close it when its PR merges, noting the implementing PR number.

### When Tracking Issues Are Warranted

Create tracking issues when a delivery plan exists —
  that is, when work spans multiple PRs and the sequencing matters.
Work small enough to fit in a single PR needs no delivery plan
  and no milestone issues;
  a plain issue (or no issue at all, for trivial changes) is enough.

### Requirements, Milestones, and PRs

These are **not** necessarily one-to-one, and conflating them causes trouble:

- A requirement is scoped to be implementable in a single PR
    (see [../product-requirements/README.md](../product-requirements/README.md)).
- A milestone also ships as a single PR.
- But a milestone may deliver *part* of a large requirement,
    or span *several* small requirements,
    or deliver infrastructure that no requirement describes on its own
    (project scaffolding, CI wiring, a contract definition).

When a milestone doesn't map cleanly onto exactly one requirement,
  say so explicitly in the milestone issue,
  and link every requirement it touches.
If a requirement repeatedly needs several milestones to deliver,
  that is a signal the requirement was sliced too thick — consider splitting it.

## Referencing Milestones in Code and Docs

Don't hard-code specific milestone identifiers (M2, M3, …) in code, comments, or project docs:
  plans shift, so those references rot.
See [`.claude/rules/delivery-milestones.md`](/.claude/rules/delivery-milestones.md) for the rule.
The delivery plan and its milestone tracking issues are the single source of truth for the
  milestone breakdown; link to them rather than restating it.

## Naming Convention

See [../README.md](../README.md) for file naming conventions
  and general document structure guidelines.

## Relationship to Other Document Types

- [**Product Vision**](../product-vision/):
  Defines high-level product direction and goals.
- [**Product Requirements**](../product-requirements/):
  Atomic, implementable requirements — the *what*.
- [**Engineering Designs**](../engineering-designs/):
  Significant technical decisions — the *how*.
- [**Delivery Plans**](../delivery-plans/) (this directory):
  Planned iterations and milestones — the *when and in what order*.
- [**Analyses**](../analyses/):
  Research and evaluations that inform design decisions.
- [**Notes**](../notes/):
  Exploratory thinking and half-baked ideas.
