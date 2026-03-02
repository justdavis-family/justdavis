# Test Automation is a Good Thing

## Principle

Automated tests are positively correlated with all four DORA metrics (Deployment Frequency, Change
  Lead Time, Change Failure Rate, and Time to Restore Service), and those DORA metrics are
  positively correlated with better business outcomes.
Invest in test automation as a core capability.

## Rationale

- **DORA research** (10+ years, thousands of organizations) shows automated testing correlates with
  elite performance across all four key metrics.
- **Elite performers** deploy multiple times daily vs. monthly for low performers, enabled by
  automated testing.
- **Change failure rates** drop 50-80% with comprehensive automated testing.
- **Business outcomes** improve: faster feature delivery, reduced production defects, better
  customer satisfaction.
- Automated tests provide fast feedback loops that enable rapid, safe iteration.

## Examples

**Good (investing in automation):**
- Automated tests run on every commit in CI/CD pipeline.
- Test suite completes quickly enough to provide feedback within minutes.
- Tests catch regressions before they reach production.
- Team can deploy confidently multiple times per day.

**Bad (underinvesting in automation):**
- Relying primarily on manual testing for regression coverage.
- Skipping tests "to move faster" - creates technical debt and slows velocity over time.
- Test suite so slow that developers skip running it locally.
- Fear of deploying because of inadequate automated coverage.

## When to Break This Rule

- **Exploratory testing** - Manual testing is valuable for discovering unexpected issues and
  evaluating UX.
- **Early prototypes** - Disposable proof-of-concept code may not warrant test automation.
- **One-off scripts** - Automation overhead may exceed value for truly one-time operations.

## Relationship to Other Principles

- Complements **60% coverage is good enough** - automation matters more than hitting arbitrary
  high coverage targets.
- Enables **inverted test pyramid** - automated e2e tests require automation infrastructure.
- Supports **fail fast and loud** - automated tests catch issues before production.

## Evidence Base

- DORA State of DevOps Research (2014-2024): Test automation identified as key capability for
  elite performers.
- Industrial studies show 307-675% ROI for test automation over 10+ cycles.
- One Fortune 500 company documented $6M additional revenue from 50% faster testing.
