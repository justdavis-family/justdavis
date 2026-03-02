# Inverted Test Pyramid: End-to-End > Integration > Unit

## Principle

Prioritize test types based on value, not dogma: **end-to-end tests > integration tests > unit
  tests**.
Focus on thoughtful, well-designed tests at each level rather than following a rigid pyramid.

## Rationale

- **Peer-reviewed research** on test pyramids is surprisingly weak - the 70/20/10 split is
  industry consensus without strong empirical validation.
- **Unit tests of simple logic** are often performative and provide minimal value.
- **Integration tests of simple glue code** likewise provide minimal value.
- **Thoughtful e2e tests** of primary user flows provide tremendous value by testing the system
  as users experience it.
- Traditional pyramids optimize for **test execution speed** at the expense of **catching real
  bugs**.

## Guidelines by Test Type

### End-to-End Tests (Highest Priority When Done Well)

**Create e2e tests for:**
- Primary user workflows and critical paths.
- Particularly tricky or failure-prone user flows.
- Features where user experience is paramount.

**Design for testability:**
- Build interfaces that can be tested quickly (test APIs, stable selectors, etc.).
- Invest in test infrastructure that makes e2e tests fast and reliable.
- Avoid thoughtless e2e tests that are slow and flaky - these waste massive developer/agent time.

**Example:** iOS app registration flow with backend integration tested end-to-end.

### Integration Tests (When Testing Complex Orchestration)

**Create integration tests for:**
- Complex glue/orchestration code that coordinates multiple components.
- Code that's **designed to be testable** (dependency injection, clear boundaries).
- Database interactions, API integrations, external service calls.

**Avoid integration tests for:**
- Simple pass-through or orchestration code.
- Code that just wires components together without logic.

**Example:** Repository layer tests with real database (via testcontainers).

### Unit Tests (When Testing Complex Logic)

**Create unit tests for:**
- Complex algorithms or business logic.
- Pure functions with many edge cases.
- Stateless transformations or calculations.

**Avoid unit tests for:**
- Simple getters, setters, or data classes.
- Trivial logic that's self-evident.
- Code that's just calling other well-tested components.

**Example:** Date/time calculation algorithms with multiple edge cases.

## When to Break This Rule

- **Performance-critical code** - Unit tests may be necessary to verify optimizations.
- **Library development** - Public APIs benefit from comprehensive unit test coverage.
- **Legacy code** - May need unit tests to refactor safely when e2e tests don't exist.

## Relationship to Other Principles

- Aligns with **YAGNI** - don't write performative tests for hypothetical value.
- Supports **60% coverage is good enough** - focus on valuable tests, not coverage percentages.
- Works with **test automation** - all test types should be automated.
- Complements **mocks are usually dumb** - prefer real components in integration tests.

## Evidence Base

- Limited peer-reviewed research on test pyramid effectiveness.
- One study of 17 Java projects found **no significant difference** in defect detection between
  unit and integration tests.
- Google's internal guidance: 80% unit tests, but Google defines "unit" by size (fast, hermetic)
  rather than scope.
- Microsoft/IBM TDD study showed 40-90% defect reduction but didn't compare test type
  distributions.

## Key Insight

**Test value matters more than test type.**
A well-designed e2e test that catches real bugs is worth 100 performative unit tests that just
  exercise getters and setters.
