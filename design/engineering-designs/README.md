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

## Where an Engineering Design Fits

An engineering design is one step in the repository's design and development process;
  see [`../README.md`](../README.md) for the full sequence and how the steps relate.

The two steps immediately either side of this one:

- Before, only as needed: an [analysis](../analyses/),
    where a decision has multiple viable options,
    so that the design can cite a conclusion rather than assert one.
  Many designs don't need one, and straightforward choices shouldn't have one.
  See [`../analyses/README.md`](../analyses/README.md) for when one is warranted.
- After: a [delivery plan](../delivery-plans/) where the design takes more than one PR to build,
    which fixes the milestones and scope boundaries before development begins.

An engineering design itself makes the concrete technology choices,
  specifies the architecture and implementation approach,
  defines configuration and setup details,
  and documents its rationale — linking back to any analysis it rests on.

## Naming Convention

See [../README.md](../README.md) for file naming conventions
  and general document structure guidelines.

## Template

Use [`template.md`](template.md) as a starting point
  for new engineering design documents.
The template includes sections for Overview, Technology Choices, Architecture,
  Configuration, Trade-offs, Success Criteria, and References.

## Relationship to Other Document Types

This directory holds the **how**: the technical approach that delivers on the requirements.
For what every other `design/` subdirectory is for, see
  [How Is the Design and Development Documentation Organized?](../README.md#how-is-the-design-and-development-documentation-organized).

Engineering design docs typically address a set of related requirements
  and should reference them in their content.
