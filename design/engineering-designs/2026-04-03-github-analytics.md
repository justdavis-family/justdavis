# GitHub Analytics Engineering Design

## Overview

Technical design for the GitHub analytics collection and reporting system.
Addresses the need to durably capture GitHub's time-limited analytics API data.
See [GitHub Analytics Data Collection](../product-vision/2026-04-03-github-analytics.md)
  for the product context and
  [GitHub Analytics Collector](../product-requirements/2026-04-03-github-analytics-collector.md)
  for the requirements.

## Technology Choices

- **Python 3.12** with `httpx` (async mode via `httpx.AsyncClient`) for GitHub API calls.
- **asyncio** for concurrent collection: all `(repo, metric)` pairs run as asyncio Tasks
    bounded by a shared `asyncio.Semaphore`.
- **structlog** for structured debug-level logging with per-task context binding.
- **uv** for package management and running Python; replaces pip/venv.
- **ruff** for linting and formatting; **mypy** (strict) for type checking.
- **pytest + pytest-recording (vcrpy) + pytest-asyncio** for tests against recorded real
    API responses, consistent with the "mocks are usually dumb" principle.
- **NDJSON** (newline-delimited JSON) for storage: human-readable,
    queryable with `jq`/`grep`, append-friendly, no binary formats.
- **Invocation chain: GitHub Actions → Mise → uv.**
    The Actions workflow delegates entirely to Mise tasks.
    Developers can run `MISE_EXPERIMENTAL=1 mise run //github-analytics:ci` locally
    and exercise the exact same code path as CI.

## Architecture

Three components:

1. **Collector** (`github-analytics/`) in this monorepo.
   Reads `config.yaml` (repo allowlist), queries the GitHub API for 9 endpoint types,
   writes idempotent NDJSON files.
   All `(repo, metric)` pairs are fetched concurrently via `asyncio.gather` bounded by
   an `asyncio.Semaphore` (default 20, matching the httpx keepalive pool).
   Exits 0 on full success, 1 if any per-repo/endpoint error occurred.

2. **Data repository** (`justdavis-family/github-analytics-data`).
   Contains only NDJSON data files and generated README reports.
   Committed to by each collection run via a PAT-authenticated git push.

3. **Scheduled workflow** (`.github/workflows/github-analytics.yml`).
   Runs daily at 06:00 UTC.
   Orchestrates checkout → collect → report → git commit → git push.
   Python handles data; Mise/bash handles git operations.
   On failure, GitHub Actions sends an email automatically.

## Data Model

Repository: `justdavis-family/github-analytics-data`.

Directory structure: `{owner}/{repo}/{metric}.ndjson`.

NDJSON formats (one JSON object per line, all timestamps ISO 8601 UTC):

- `views.ndjson` / `clones.ndjson`: `{"date": "YYYY-MM-DD", "count": N, "uniques": N}`.
- `referrers.ndjson`: `{"date": "YYYY-MM-DD", "referrer": "...", "count": N, "uniques": N}`.
- `paths.ndjson`: `{"date": "YYYY-MM-DD", "path": "...", "title": "...", "count": N, "uniques": N}`.
- `stars.ndjson`: `{"starred_at": "...", "user": "..."}`.
- `forks.ndjson`: `{"forked_at": "...", "owner": "..."}`.
- `releases.ndjson`: `{"date": "YYYY-MM-DD", "tag": "...", "asset": "...", "download_count": N}`.
- `metadata.ndjson`: `{"date": "YYYY-MM-DD", "stars": N, "forks": N, "watchers": N,
    "open_issues": N, "network_count": N|null, "subscribers": N|null, "size_kb": N|null}`.
- `workflow_runs.ndjson`: `{"date": "YYYY-MM-DD", "name": "...", "path": "...",
    "workflow_id": N, "status": "...", "conclusion": "...",
    "completed_count": N, "incomplete_count": N, "avg_duration_seconds": F|null}`.

## Configuration

`github-analytics/config.yaml` contains only the repo allowlist.
Supported patterns: `org:<name>`, `user:<name>`, `<owner>/<repo>`.
Collection frequency is controlled by the GitHub Actions cron schedule.

Endpoints collected for every repo:
`views`, `clones`, `referrers`, `paths`, `stars`, `forks`, `releases`, `metadata`,
`workflow_runs`.

The `--max-concurrent` CLI flag (default 20) controls the maximum number of concurrent
HTTP requests in flight, tied to the httpx keepalive connection pool size.

## GitHub PAT Requirements

`ANALYTICS_DATA_PAT` must be a classic PAT (not fine-grained) with `repo` scope,
  created by the `karlmdavis` account.
The GitHub Traffic API requires push access to the queried repo,
  which cannot be expressed as a fine-grained permission across many repos.
The same PAT is used for pushing to the data repository.

## Concurrency

All `(repo, metric)` pairs are launched as asyncio Tasks via `asyncio.gather`.
A shared `asyncio.Semaphore(N)` wraps only the `await client.get(...)` call —
not retries or compute — so the semaphore is held only for the HTTP round-trip.
`N` defaults to 20 and matches `httpx.Limits(max_keepalive_connections=N, max_connections=N)`,
ensuring the semaphore and connection pool are always coherent.

Safety properties:
- Single-threaded event loop: no concurrent mutation of shared state.
- Each `(repo, metric)` task writes to a unique file path: no file contention.
- `writer.append_records` uses atomic temp-file-then-rename: safe to call from any task.

## Observability

**Debug logging** (`--verbose` flag): `structlog` events bound with `repo` and `metric`
context per task.
Events include `fetch.start`, `fetch.done` (with `records`, `io_ms`), and `retry`
(with `attempt`, `wait_s`).
Output is suppressed by default; enabled with `--verbose`.

**INFO-level progress** (always shown): plain `print()` for human-readable output.
- Header line: `Collecting N repos (M concurrent max)...`
- Per-repo completion: `  ✔ owner/repo    8.2s  (views:14 stars:312 ...)`
    or `  ✗ owner/repo    ERROR: <message>` on failure.
- Footer: `Done in Xs.`

**Timing summary** (always shown after collection):
A table printed to stdout showing I/O, wait, and compute seconds per endpoint,
plus totals.
Timing buckets:
- **I/O**: time inside `await client.get(...)`.
- **Wait**: time inside `await asyncio.sleep(...)` (rate-limit retries only).
- **Compute**: everything else (JSON parsing, deduplication, file writes).
Accumulated per metric name in a shared dict — safe because asyncio is single-threaded.

## Error Handling

- Per-repo and per-endpoint failures are isolated via `asyncio.gather(return_exceptions=True)`.
- Errors are collected across all tasks and reported after all tasks complete.
- Collector exits 1 if any error occurred; git operations still run to commit partial data.
- Rate limits: primary (429) and secondary (403 with `Retry-After`/`abuse`) are retried
    with exponential backoff up to 3 attempts, sleeping with `await asyncio.sleep`.
- Concurrent workflow runs are serialized via `concurrency: group: analytics-collection`.

## Storage Estimate

Based on actual API response sizes sampled from `karlmdavis` repos:
~535 bytes/repo/day on average.
Projected 5-year total (42 current repos + 2/year): ~45 MB in the data repository.
This is 4.5% of GitHub's 1 GB repository size guideline.

## Trade-offs

| Approach | Chosen | Reason |
|---|---|---|
| Separate data repo vs. same repo | Separate | Keeps monorepo commit history clean; own 1 GB limit |
| NDJSON vs. SQLite | NDJSON | Human-readable; queryable with standard CLI tools; no binary diffs |
| Cron-on-homelab vs. GitHub Actions | GitHub Actions | Zero infrastructure; managed reliability; built-in failure email |
| Classic PAT vs. fine-grained | Classic | Traffic API requires push access; fine-grained impractical at 42+ repos |

## Success Criteria

- `MISE_EXPERIMENTAL=1 mise run //github-analytics:ci` passes with all tests green,
    lint clean, and mypy strict satisfied.
- Manual workflow run populates the data repository with NDJSON files and rendered READMEs.
- Running the collector twice on the same day produces no duplicate records.
- `collect` prints a timing summary table on exit showing I/O, wait, and compute seconds.
- Total collection runtime for a typical repo set completes well under 5 minutes on GitHub
    Actions, staying within the 5% budget of 3,000 monthly Actions minutes.

## References

- **Product Requirements**:
    [GitHub Analytics Collector](../product-requirements/2026-04-03-github-analytics-collector.md).
