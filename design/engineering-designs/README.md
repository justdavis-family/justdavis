# Engineering Design Documents

This directory contains engineering and technical design specifications for projects in this monorepo.

## Purpose

Engineering design documents capture technical implementation decisions including:

- Technology stack choices (frameworks, libraries, tools).
- Architecture patterns and system design.
- Infrastructure setup and deployment configuration.
- Development tooling and workflow design.
- Technical constraints and trade-offs.

These documents focus on **how** we build the system and **what technologies** we use,
  complementing [product vision documents](../product-vision/),
  which focus on **why** to build something
  and [product requirements](../product-requirements/),
  which focus on **what** to build.

## When to Create an Engineering Design Document

Create an engineering design document when:

- Making significant technology stack decisions (choosing between frameworks, databases, etc.).
- Designing system architecture or major architectural changes.
- Establishing infrastructure patterns (CI/CD, deployment, monitoring).
- Defining development workflows and tooling standards.
- Making cross-cutting technical decisions that affect the entire codebase.

## Design Process

Engineering design decisions should generally be preceded by analysis:

1. **Analysis phase** ([analyses/](../analyses/)):
   - Research available options and alternatives.
   - Evaluate trade-offs between different approaches.
   - Document findings and recommendations.
   - Example: "Analysis: PostgreSQL ORM Options (Diesel vs SQLx vs SeaORM)".

2. **Design phase** (this directory):
   - Make concrete technology choices based on analysis.
   - Specify architecture patterns and implementation approach.
   - Define configuration and setup details.
   - Document rationale linking back to analysis.

3. **Implementation phase** ([implementation-plans/](../implementation-plans/)):
   - Break design into concrete implementation tasks.
   - Specify exact file changes and code structure.
   - Create step-by-step implementation guide.

Not all engineering decisions require formal analysis documents (especially straightforward choices),
  but significant decisions with multiple viable options should be analyzed before design.

## Naming Convention

See [../README.md](../README.md) for file naming conventions
  and general document structure guidelines.

## Template

Use [`template.md`](template.md) as a starting point
  for new engineering design documents.
The template includes sections for Overview, Technology Choices, Architecture,
  Configuration, Trade-offs, Success Criteria, and References.

## Relationship to Other Document Types

- [**Product Vision**](../product-vision/):
  Defines high-level product direction and goals.
- [**Product Requirements**](../product-requirements/):
  Atomic, implementable requirements.
- [**Engineering Designs**](../engineering-designs/) (this directory):
  Defines technical implementation approach.
- [**Implementation Plans**](../implementation-plans/):
  Breaks designs into actionable tasks.
- [**Analyses**](../analyses/):
  Evaluates options to inform design decisions.
- [**Notes**](../notes/):
  Exploratory thinking and broader technical concepts.

The typical flow is:
  Product Vision → Product Requirements → Engineering Design → Implementation Plans → Code.

Engineering design docs typically address a set of related requirements
  and should reference them in their content.
