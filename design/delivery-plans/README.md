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

### What Earns a Tracking Issue

**Only work that is concrete and shippable gets a *design-process* tracking issue.**
A delivery plan is the first artifact in the design process that qualifies:
  it commits to a fixed list of milestones, each with acceptance criteria and a merge event.
Everything upstream of it — analyses, the vision, requirements, engineering designs — is *thinking*.

That does not mean the thinking goes untracked.
A rough idea often has a task somewhere long before it has a plan,
  and a plain GitHub issue is a perfectly good home for one.
What it should *not* have is an issue per design document.

Two issue types come out of that:

| Issue | Type | Title format | Represents |
|---|---|---|---|
| Delivery plan | `Delivery Plan` | `<Project> — <plan title>` | A delivery plan, as a container for its milestones. |
| Milestone | `Milestone` | `<Project> M<N> — <milestone title>` | One milestone, delivered by one PR. |

Milestone issues are **GitHub sub-issues of the delivery-plan issue**,
  which gives the plan issue a rollup progress view across its milestones.

Deliberately excluded:

- **No vision issues.**
  A vision is inspirational rather than deliverable; it has no done-state,
    so an issue for it would stay open forever and track nothing.
- **No requirement issues.**
  Requirements *do* carry acceptance criteria, so this is not a "nothing to track" case —
    it is a redundancy case.
  A requirement's acceptance criteria are satisfied *through* the milestones that deliver it,
    so a requirement issue would duplicate the status its milestone issues already report.
  A requirement's own lifecycle lives in its document's `status:` frontmatter,
    updated by the PR that implements it.
- **No engineering-design or analysis issues**, for the same reason as visions:
    they are reasoning, not deliverables.

Revisit these exclusions if a concrete use case appears that the milestone issues cannot serve.

### How an Idea Becomes Tracked Work

Tracking issues are not created as a batch of paperwork when the design docs land.
The tracker follows the work as it matures:

1. A rough idea gets captured as an ordinary task — a plain GitHub issue,
     a Todoist task, a line in a daily note, or nothing at all.
   Which of those it is doesn't matter yet.
2. Over days or weeks it is refined — into analyses, then a vision,
     then requirements and engineering designs.
   Throughout, it stays **one** task.
   Nothing is created per document.
3. When a delivery plan lands, a `Delivery Plan` issue exists for it,
     with milestone sub-issues underneath.

Step 3 has two paths, and neither is more correct than the other:

- If the idea was already tracked as a GitHub issue,
    **relabel and rewrite that issue in place** rather than opening a new one.
  The task you already had matures into the container for the work it turned out to require,
    and its history and any discussion on it come along.
- If it was tracked elsewhere, or not at all, **create the delivery-plan issue fresh.**

The thing to avoid is not "creating an issue late" — it is creating one *per design document*.

### The Delivery-Plan Issue Is Not the Delivery Plan

The plan **document** stays in `design/`.
It is versioned, reviewed through a PR, and accumulates the record of *why* the sequence is what it is
  — including how it was resequenced along the way.
None of that survives in an issue.

The plan **issue** is a *container*: a pointer to the document, plus the milestone sub-issues.
It does not restate the plan's content, and it closes cleanly when its last milestone closes.

### What a Milestone Issue Contains

A milestone issue links to the delivery plan, names which milestone it tracks,
  restates that milestone's deliverable briefly,
  and **copies its acceptance-criteria checklist** so progress can be ticked off as work proceeds.
The checklist is authored in the delivery plan and is authoritative there;
  the issue's copy is a convenience for tracking, not a second source of truth.
Close the issue when its PR merges, noting the implementing PR number.

### Sequencing and Cross-Links Use Issue Relationships

Milestones are sequenced, and they relate to requirements many-to-many.
Both facts are recorded as **GitHub issue relationships**, not as prose:

- A milestone that cannot start until another finishes is marked **blocked by** it.
- A milestone that delivers part of a requirement links to that requirement's *document*;
    since requirements have no issues, there is nothing to link to in the tracker.

Recording the blocking relationships is what makes creating every milestone sub-issue up front
  workable rather than noisy:
  unstarted milestones are *visibly blocked*,
  so a query for actionable work skips them automatically,
  and the plan issue's rollup still counts them.
If those relationships are ever dropped,
  the up-front sub-issues become a queue of speculative work that resequencing invalidates —
  so the two conventions stand or fall together.

### Milestones, Requirements, and PRs

These are **not** one-to-one, and conflating them causes trouble:

- A requirement should generally be scoped to be implementable in a single PR
    (see [../product-requirements/README.md](../product-requirements/README.md)).
- A milestone also ships as a single PR.
- But a milestone may deliver *part* of a large requirement,
    or span *several* small requirements,
    or deliver infrastructure that no requirement describes on its own
    (project scaffolding, CI wiring, a contract definition).

When a milestone doesn't map cleanly onto exactly one requirement,
  say so explicitly in the milestone's section of the plan,
  and link every requirement document it touches.
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
