# Engineering Principles

This project's engineering principles are detailed in the @design/engineering-principles/ directory.

When designing solutions or choosing between options, consider these engineering principles.
During design discussions, watch for generalizable patterns that could become
  new engineering principles, or refinements to existing engineering principles.

## Current Engineering Principles Index

### Core Development Principles

- [YAGNI](/design/engineering-principles/2026-01-06-yagni.md):
  Don't build features or abstractions before they're needed.
- [Strong Typing and Information Preservation](/design/engineering-principles/2026-01-07-strong-typing.md):
  Use type systems to preserve all available information.
- [Comprehensive Error Modeling](/design/engineering-principles/2026-01-08-error-modeling.md):
  Model all errors explicitly; never suppress error information.
- [Fail Fast and Loud](/design/engineering-principles/2026-01-09-fail-fast.md):
  Crash immediately on impossible states with clear messages.

### Testing Principles

- [Test Automation is a Good Thing](/design/engineering-principles/2026-01-12-test-automation.md):
  Automated tests correlate with DORA metrics and business outcomes.
- [60% Automated Test Coverage is Good Enough](/design/engineering-principles/2026-01-13-60-percent-coverage.md):
  Use 60% branch coverage as minimum; no strong evidence for higher targets.
- [Inverted Test Pyramid](/design/engineering-principles/2026-01-14-inverted-test-pyramid.md):
  Prioritize e2e > integration > unit tests, based on value, not dogma.
- [Mocks are Usually Dumb](/design/engineering-principles/2026-01-15-avoid-mocks.md):
  Prefer real components; use mocks only for external services or with good reason.
