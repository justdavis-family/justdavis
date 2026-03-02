# Product Requirements

Atomic, implementable requirements for projects in this monorepo.

## Purpose

Product requirements break down vision into deliverable units.
Each requirement represents a single user story that can be fully implemented in one PR.

**Key distinction from vision docs:**

- Vision docs (`product-vision/`) capture long-term direction and stay stable over time.
- Requirements capture tactical breakdown
    and absorb scope changes through new requirements
    rather than editing vision docs.

## Requirement Format

Requirements use both YAML frontmatter (machine-readable) and Markdown body (human-readable) to
  support tooling and direct reading.

See [../README.md](../README.md) for file naming conventions
  and general document structure guidelines.

### Template

Use [`template.md`](template.md) as a starting point for new requirement documents.
The template includes YAML frontmatter for machine-readable metadata
  and a Markdown body with Summary, User Story, Acceptance Criteria,
  and References sections.

## Granularity Principles

**One user story per requirement.**
If a requirement has more than one user story, ask yourself:
  "would it be safer to break this into multiple separate requirements?"

**Goal:**
Requirements should be atomic enough that a PR rarely partially implements them.

**Test coverage is part of done:**
Each requirement's acceptance criteria must include test coverage.
We can automate quality *checks* (CI gates, coverage thresholds) in follow-on requirements,
  but the quality itself ships with the feature.

**Examples of good granularity:**

- "Hello World" API endpoint.
- Local build automation for API.
- CI system that builds and tests API.

**Signs a requirement is too big:**

- Multiple user stories.
- Acceptance criteria span unrelated areas.
- A PR might reasonably implement only part of it.

## Lifecycle

### Status Values

- **draft** — Requirement is being designed.
  Can be edited freely during this phase.
- **implemented** — Requirement has been implemented and merged.
  Becomes immutable; changes require new requirements.
- **superseded** — Requirement has been replaced by a newer requirement.
  The `replaces` field in the newer requirement links back.

### Requirement Relationships

- **depends_on** — Must be implemented before this requirement.
- **extends** — Adds new scenarios or capabilities to an existing requirement.
- **modifies** — Amends the meaning or behavior of an existing requirement.
- **replaces** — Supersedes an existing requirement entirely.

### Workflow

1. Create requirement in `draft` status.
2. Refine user story and acceptance criteria.
3. Implement and link PR(s).
4. Mark as `implemented` when merged.
5. Future changes create new requirements with `extends` or `replaces` relationships.

## Cross-Linking

Requirements should be cross-linked with:

- **Vision docs** — Which vision this requirement implements.
- **Engineering design docs** — Technical approach for implementation.
- **PRs** — Actual implementation artifacts.
- **Related requirements** — Dependencies, extensions, replacements.

Both the YAML frontmatter and the References section
  should contain this information for machine and human consumption.

## What Should Be a Requirement

**Include (product-impacting work):**

- User-facing features and capabilities.
- Foundational engineering that enables features.
- Quality and observability improvements.

**Exclude (meta-work about how we develop):**

- Process documentation (this requirements process itself, contribution guidelines, retrospectives).
- Project setup and configuration (repo structure, CLAUDE.md, editor configs).
- Meeting notes and decision logs.

**Litmus test:** Does this work affect the product's capabilities or quality for users?
If yes, it's a requirement.
If it only affects how developers work on the product, it's not.
