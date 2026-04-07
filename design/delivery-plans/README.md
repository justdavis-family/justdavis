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
- **Honest deferral**: if something feels nice-to-have, put it in a later milestone
    (or drop it entirely) rather than bundling it into the first cut.
- **Human decisions recorded**: the plan captures choices about sequencing and scope
    that aren't obvious from the requirements themselves.

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
