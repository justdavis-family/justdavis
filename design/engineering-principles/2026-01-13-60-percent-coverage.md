# 60% Automated Test Coverage is Good Enough

## Principle

There is not strong scientific evidence that higher test coverage produces better outcomes.
We use **60% branch coverage** as our minimum threshold: builds should fail in CI if total test
  coverage drops below this level.

## Rationale

- **Industry research** consistently identifies 70-80% as the "sweet spot" for ROI, with
  diminishing returns beyond that.
- **ACM ICSE 2014 study** found only low to moderate correlation between coverage and
  effectiveness, challenging assumptions that higher coverage automatically means better quality.
- **Effort curve** shows that moving from 80% to 100% requires disproportionately more effort for
  progressively less valuable returns.
- **60% provides safety net** while avoiding the trap of chasing coverage percentages for their
  own sake.
- Coverage is a **necessary but insufficient** measure of test quality - 100% coverage doesn't
  guarantee good tests.

## Examples

**Good (coverage as a baseline, not a goal):**
- Maintain 60%+ coverage to ensure basic safety net.
- Focus on testing critical paths and complex logic thoroughly.
- Write meaningful tests that catch real bugs, not just hit coverage targets.
- Use coverage to find untested code, not as a quality metric.

**Bad (coverage theater):**
- Writing trivial tests just to hit 90%+ coverage targets.
- Celebrating high coverage while tests don't catch actual bugs.
- Spending weeks getting from 95% to 100% coverage.
- Using coverage as the primary measure of test quality.

## When to Break This Rule

- **Critical infrastructure** - Payment processing, security, data integrity code may warrant
  higher coverage.
- **Public APIs** - External interfaces benefit from comprehensive test coverage.
- **New code** - Setting higher coverage targets (70-80%) for new code while allowing lower
  coverage on legacy code.

## CI Enforcement

**Builds fail if branch coverage < 60%:**
- Prevents coverage from degrading over time.
- Creates minimum quality bar without being oppressive.
- Allows teams to focus on meaningful tests rather than coverage percentages.

## Relationship to Other Principles

- Works with **test automation** - automated coverage checking in CI pipeline.
- Supports **inverted test pyramid** - focus on valuable tests, not coverage numbers.
- Aligns with **YAGNI** - don't build tests for hypothetical edge cases just to hit coverage
  targets.

## Evidence Base

- Google internal standards: 60% acceptable, 75% commendable, 80% gating standard.
- Industry consensus: 70-80% sweet spot with diminishing returns beyond.
- Research shows effort to reach 95-100% can be disproportionate (one case: 2 years for final 5%).
- ACM ICSE 2014: Coverage correlation with effectiveness is weaker than commonly assumed.
