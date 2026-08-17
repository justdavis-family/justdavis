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

Routing only. Every rule lives in the linked documents — read the one you need and follow it there.

## First: Does This Work Need the Process at All?

New features and significant enhancements do; simple bug fixes, maintenance, and infrastructure
  changes go straight to implementation
  — see [When Should the Design Process Be Followed?](../../../design/README.md#when-should-the-design-process-be-followed).

Don't over-apply this. A one-line fix does not need a vision document.

## The Sequence

Work forward through these; skip a step only when you can say why it doesn't apply.
Read each directory's `README.md` before writing that document — it defines what belongs there.

| Step | Directory | Rules | Template |
|---|---|---|---|
| 1. Analysis *(when needed)* | `design/analyses/` | [README](../../../design/analyses/README.md) | none — see existing analyses |
| 2. Product Vision | `design/product-vision/` | [README](../../../design/product-vision/README.md) | [template.md](../../../design/product-vision/template.md) |
| 3. Product Requirements | `design/product-requirements/` | [README](../../../design/product-requirements/README.md) | [template.md](../../../design/product-requirements/template.md) |
| 4. Engineering Design | `design/engineering-designs/` | [README](../../../design/engineering-designs/README.md) | [template.md](../../../design/engineering-designs/template.md) |
| 5. Delivery Plan *(when multi-PR)* | `design/delivery-plans/` | [README](../../../design/delivery-plans/README.md) | [template.md](../../../design/delivery-plans/template.md) |

Supporting types outside the sequence:
  [engineering principles](../../../design/engineering-principles/README.md) — cross-cutting standards,
  indexed in [`.claude/rules/engineering-principles.md`](../../rules/engineering-principles.md);
  and [notes](../../../design/notes/) — half-baked ideas.

Also read: [`design/README.md`](../../../design/README.md) for the workflow overview and naming
  conventions, [`.claude/rules/markdown-style.md`](../../rules/markdown-style.md) for formatting,
  [`.claude/rules/pr-workflow.md`](../../rules/pr-workflow.md) for shipping, and
  [`.claude/rules/delivery-milestones.md`](../../rules/delivery-milestones.md) before naming a
  milestone anywhere outside the delivery plan.

## Authoring a Full Lineage

Writing several of these documents for one project has its own conventions —
  one PR with a commit per document, worktree setup,
  and letting each document constrain the next.
Read
  [How Do I Author a Full Set of These Documents?](../../../design/README.md#how-do-i-author-a-full-set-of-these-documents)
  before starting.

Tracking issues are **not** created per document — they start at the delivery plan.
See [`design/delivery-plans/README.md`](../../../design/delivery-plans/README.md).
