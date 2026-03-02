# Mocks are Usually Dumb

## Principle

Unless you have a damned good reason, avoid mocks in tests.
Prefer using real components, real databases (via containers), and real integrations.

## Rationale

- **Mocks test your mocks, not your code** - They verify that your code calls the mock correctly,
  not that it works with the real dependency.
- **Mocks diverge from reality** - As real services evolve, mocks become stale and tests pass
  while production breaks.
- **Mocks add maintenance burden** - You must maintain both the real implementation and the mock
  implementation.
- **Real components are often practical** - With modern tools (Docker, testcontainers), using real
  databases and services is often straightforward.
- **Integration bugs are missed** - Mocks hide integration issues that only appear when
  components interact.

## What Counts as a Good Reason

### 1. External Services with VCR-Style Mocks

**When:**
- Testing code that calls external services or platform libraries you can't run locally.
- Service has rate limits, costs money, or requires authentication.

**How:**
- Create mock versions that use a **VCR (Video Cassette Recorder) approach**.
- When passed real (recorded) requests, return real (recorded) responses.
- Record real interactions once, replay them in tests.

**Example:**
- Mock for Stripe API that replays real API responses.
- Mock for iOS platform APIs that returns real platform data.

### 2. Integration Tests for Complex Orchestration

**When:**
- Testing complex orchestration code where you have a **good reason** you can't use real
  components.
- The orchestration logic itself is complex enough to warrant isolated testing.

**Example:**
- Testing a workflow engine that coordinates multiple services where real services would make
  tests too slow or flaky.

## Examples

**Good (avoiding mocks):**
- Use testcontainers for database tests (PostgreSQL in Docker).
- Call real internal services/modules in integration tests.
- Use real HTTP client in tests, mock the HTTP server if needed.
- Test against real filesystem, not mocked file operations.

**Bad (mock abuse):**
- Mocking database calls in integration tests - use testcontainers instead.
- Mocking internal service calls - use the real service.
- Hand-coded mocks that don't reflect real behavior.
- Mocking getters/setters or simple data classes.

**Acceptable (good reasons):**
- VCR-style mock for Stripe API with recorded real responses.
- Mock for expensive ML model inference in tests.
- Mock for external SMS service that charges per message.

## When to Break This Rule

- **External paid services** - Don't rack up AWS bills in tests.
- **Services with rate limits** - Don't hit GitHub API limits.
- **Hardware dependencies** - Can't test Bluetooth without device.
- **Performance tests** - Sometimes need controlled, repeatable mock responses.

## Relationship to Other Principles

- Supports **inverted test pyramid** - real components make integration/e2e tests more valuable.
- Complements **test automation** - real components in automated tests catch real bugs.
- Aligns with **fail fast** - tests with real components fail when actual integrations break.

## Key Insight

**If you can use the real thing in tests, use the real thing.**
Modern tooling (Docker, testcontainers, in-memory databases) makes this practical for most
  dependencies.
Only reach for mocks when the real dependency is genuinely impractical to use in tests.
