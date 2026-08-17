# Product Vision Documents

High-level product vision and direction for projects in this monorepo.

## Purpose

Vision documents capture **why** we're building something and the long-term direction, focusing on:

- User problems and needs being addressed.
- Feature concepts and user-facing capabilities.
- Business value and product goals.
- Success metrics from user and business perspective.
- User workflows and experience design.

**Key distinction from requirements:**
Vision docs are aspirational and are more likely to stay stable over time;
  their focus on big-picture goals means that
  they're less likely to suffer from scope changes or failed experimentation.
Each vision should be broken down into atomic requirements
  in [product-requirements](../product-requirements/),
  which handle the tactical breakdown
  and capture scope changes through new requirements.

## Template

Use [`template.md`](template.md) as a starting point for new vision documents.
The template includes sections for Problem and Motivation, Vision,
  Success Metrics, and Requirements tracking.

## Priority Annotations

Vision documents may annotate each requirement in the Requirements list
  with a parenthetical priority label that captures its standing in the broader vision:

- `(must have)` — required for the vision to be considered delivered.
- `(nice to have)` — improves the vision but the vision can be delivered without it.
- `(stretch)` — aspirational;
    will be delivered if time and circumstances permit but is not required.

These labels are advisory and live alongside the requirement's `status` field,
  which captures lifecycle state (`draft`, `implemented`, `superseded`).

## File Naming Convention

See [../README.md](../README.md) for file naming conventions
  and general document structure guidelines.
