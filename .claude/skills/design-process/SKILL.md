---
name: design-process
description: >-
  Routes you through this monorepo's design process — analysis, product vision, product requirements,
  engineering design, and delivery plan — and to the templates, conventions, and tracking issues each
  step needs. Use this whenever starting a new project, feature, or significant enhancement in this
  repo; whenever writing or reviewing anything under `design/`; whenever asked to "write a design doc",
  "plan out" a feature, or "follow the design process"; and whenever you are about to start
  implementing something substantial and are not sure whether design docs should come first.
---

# Design Process

This repo drives non-trivial work through a documented design process.
This skill tells you **which document to write, in what order, and where its rules live**.

The authoritative content lives in `design/` — this skill routes, it does not restate.
When this skill and a `README.md` disagree, the README wins;
  fix the skill.

## First: does this work need the process at all?

- **New features and significant enhancements** — yes, design docs come before (or alongside) the code.
- **Simple bug fixes, maintenance, and infrastructure changes** — no, go straight to implementation.

Don't over-apply this. A one-line fix does not need a vision document.

## The sequence

Work forward through these. Skip a step only when you can say why it doesn't apply.

| Step | Directory | Rules | Template |
|---|---|---|---|
| 1. Analysis *(when needed)* | `design/analyses/` | [README](../../../design/analyses/README.md) | none — see existing analyses |
| 2. Product Vision | `design/product-vision/` | [README](../../../design/product-vision/README.md) | [template.md](../../../design/product-vision/template.md) |
| 3. Product Requirements | `design/product-requirements/` | [README](../../../design/product-requirements/README.md) | [template.md](../../../design/product-requirements/template.md) |
| 4. Engineering Design | `design/engineering-designs/` | [README](../../../design/engineering-designs/README.md) | [template.md](../../../design/engineering-designs/template.md) |
| 5. Delivery Plan *(when multi-PR)* | `design/delivery-plans/` | [README](../../../design/delivery-plans/README.md) | [template.md](../../../design/delivery-plans/template.md) |

[`design/README.md`](../../../design/README.md) has the full workflow diagram and the naming conventions.

Two supporting document types sit outside the sequence:

- [`design/engineering-principles/`](../../../design/engineering-principles/README.md) —
    cross-cutting standards that designs and code should align with.
  Consult the index in [`.claude/rules/engineering-principles.md`](../../rules/engineering-principles.md)
    while designing; add a principle only when it is generalizable, non-obvious, and has real trade-offs.
- [`design/notes/`](../../../design/notes/) — half-baked ideas that aren't ready to be anything else.

## When to write an analysis

Analyses come *before* design decisions, and exist to evaluate options.
Write one when a significant decision has multiple viable options,
  or when the design depends on facts you'd otherwise be guessing at
  (an undocumented file format, a third-party API's real behavior, whether an approach is even feasible).

Straightforward choices don't need one.
The test is whether a reader would otherwise have to take your conclusion on faith.

Analyses are durable and committed — they explain *why* a design is what it is,
  long after the alternatives have been forgotten.
If a claim in an analysis was inherited from elsewhere rather than verified,
  say so explicitly and say what would settle it.

## Distinctions that are easy to get wrong

These trip people up repeatedly, so check yourself against them.

**A requirement is one user story that fits in one PR.**
The litmus test is: *does this affect the product's capabilities or quality for users?*
If yes, it's a requirement.
If it only affects how developers work on the product, it isn't —
  process docs, repo setup, and agent instructions are not requirements.
Signs a requirement is too big: it contains multiple user stories,
  its acceptance criteria span unrelated areas,
  or a PR could reasonably implement only part of it.
Once implemented, requirements are immutable —
  supersede them with new, cross-linked ones rather than editing them.

**A delivery plan is not a task list.**
It answers "what are the milestones, and what does each one deliver?" —
  not the steps inside each PR, which are left to whoever does the work.
Its real value is scope management: deciding what goes in each PR *before* development,
  so over-commitment surfaces early.

**Milestones must be thin vertical slices.**
Each one delivers something independently usable,
  not an intermediate state that only makes sense in hindsight.
A good test: could the reader stop after any milestone and still have something worth having?

**An engineering design is evergreen; a requirement is a snapshot.**
Update designs as the system evolves.
Don't retroactively edit implemented requirements.

## Naming and formatting

- Single-file: `YYYY-MM-DD-short-name.md`.
  Multi-file: a `YYYY-MM-DD-short-name/` directory with `README.md` as the main document.
- Title ≤10 words; short name 3–5 kebab-case words condensing the title;
    ISO 8601 dates; kebab-case throughout.
- Every document ends with a `References` section cross-linking the others by relative path.
  The templates show the expected shape.
- Follow [`.claude/rules/markdown-style.md`](../../rules/markdown-style.md) —
    one sentence per line, 110-character wrap, two-space continuation indent, periods on list items.
  This is enforced by review, and it makes prose diffs readable.

## Tracking and shipping the work

- **Tracking issues** mirror the documents: a `vision` issue, a `requirement` issue,
    and — when there's a delivery plan — one `milestone` sub-issue per milestone.
  Documents are authoritative for *content*; issues for *status*.
  Formats and structure are in
    [`design/delivery-plans/README.md`](../../../design/delivery-plans/README.md).
- **Don't hard-code future milestone identifiers** in code, comments, or long-lived docs — plans shift.
  See [`.claude/rules/delivery-milestones.md`](../../rules/delivery-milestones.md)
    for exactly where naming a milestone is and isn't acceptable.
- **Everything ships through a PR**, including design docs.
  See [`.claude/rules/pr-workflow.md`](../../rules/pr-workflow.md)
    for branch naming, the required PR description outline, the Success Criteria checklist,
    and the squash-merge convention.

## Authoring a full lineage

When writing several documents for one project, prefer **one PR with a commit per document**,
  pausing for review between them.
Each document constrains the next,
  so a review that lands after the whole set is written is a review that arrives too late to help.

Work in a git worktree under `.claude/worktrees/<branch>/` (already gitignored) to keep the
  main checkout usable.
Check `.worktreeinclude` for gitignored files that need copying into new worktrees.

Write documents in dependency order and let each one genuinely constrain the next.
If while writing a requirement you find the vision doesn't support it,
  fix the vision rather than quietly widening the requirement.
That backpressure is the point of the sequence.
