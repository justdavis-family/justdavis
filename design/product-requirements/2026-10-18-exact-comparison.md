---
title: Exact Comparison of Shared Content
status: draft
vision:
  - 2026-09-04-design-process-sync
depends_on:
  - 2026-10-18-agent-assisted-sync
extends:
  - 2026-10-18-agent-assisted-sync
modifies: []
replaces: []
engineering_designs:
  - 2026-10-13-lockstep.md
prs: []
---

# Exact Comparison of Shared Content

## Summary

The [agent-assisted sync](2026-10-18-agent-assisted-sync.md) finds differences by reading.
That is slow, costs tokens on every run, and can miss something,
  and there is no way to ask "are we in sync?" without starting a session.
This requirement replaces the reading with a command.
The declaration of what is shared becomes something a tool can read without ceasing to be
  something a person can,
  and the tool reports, per shared path, exactly how the two sides stand, in a second,
  without an agent.
The skill then starts from that report rather than from its own survey,
  and anyone can run the command to learn where the two repositories differ.

## User Story

As the maintainer of either repository,
  I want to learn in one command, without an agent,
  exactly which shared paths differ between the two repositories and how,
  so that I can trust the answer, run it as often as I like,
  and give the skill a precise starting point.

## Acceptance Criteria

### The Declaration

- [ ] The declaration of what is shared is read by the tool and by people alike,
        and stays the one place that says what the shared set is.
- [ ] A declared path that does not exist on one side is reported as missing there, never skipped.

### The Report

- [ ] For each declared path the report gives exactly one of:
        identical, differs, missing in the working repository, or missing in the other repository.
- [ ] Each side of the comparison is a specific ref, resolved to a commit and recorded in the report;
        by default the working side is the checked-out revision and the other side is its default
        branch, and either can be overridden.
- [ ] Uncommitted changes in either working tree are reported as present and excluded from the
        comparison, never silently included.
- [ ] A failure to compare a path is reported as a failure, never as identical.
- [ ] Every reference from shared content — Markdown links, `@`-imports, and skill pointers —
        that does not resolve in the working repository is reported with its file and line.
- [ ] The command runs without an agent and needs no credential beyond the git access the
        maintainer already has to both repositories.
- [ ] The command's own failure is distinguishable from any comparison result,
        by a person and by automation, and says what went wrong and where.

### The Skill Starts from the Report

- [ ] The skill explains and carries exactly the differences the report lists,
        and does not survey the repositories on its own.
- [ ] Against a report that lists no differences and no dangling references,
        the skill creates nothing and says so.

### Documentation

- [ ] `.lockstep/README.md` covers the command: how to run it, how to read its report,
        and how to override the refs it compares.

## References

### Vision

- [Shared Content in Lockstep across Two Repositories](../product-vision/2026-09-04-design-process-sync.md) —
    Whether the two repositories are in sync, and where they are not,
    can be told from either one without going looking.

### Engineering Design

- [Lockstep Engineering Design](../engineering-designs/2026-10-13-lockstep.md) —
    The split between deterministic tools and the agent,
    and how the declaration is shaped so that a tool can read it.

### Related Requirements

- [Agent-Assisted Sync of Shared Content](2026-10-18-agent-assisted-sync.md) —
    This requirement extends it, replacing the agent's survey with the tool's report.
- [Exact Delivery of a Sync](2026-10-18-exact-delivery.md) extends this requirement.

### Implementation

- None yet.
