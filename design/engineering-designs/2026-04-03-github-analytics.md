# GitHub Analytics Engineering Design

## Overview

Technical design for the GitHub analytics collection and reporting system.
Addresses the need to durably capture GitHub's time-limited analytics API data.
See [GitHub Analytics Data Collection](../product-vision/2026-04-03-github-analytics.md)
  for the product context and
  [GitHub Analytics Collector](../product-requirements/2026-04-03-github-analytics-collector.md)
  for the requirements.

## Technology Choices

- **Python 3.12** with `httpx` for GitHub API calls (async-capable, modern API).
- **uv** for package management and running Python; replaces pip/venv.
- **ruff** for linting and formatting; **mypy** (strict) for type checking.
- **pytest + pytest-recording (vcrpy)** for tests against recorded real API responses,
    consistent with the "mocks are usually dumb" principle.
- **NDJSON** (newline-delimited JSON) for storage: human-readable,
    queryable with `jq`/`grep`, append-friendly, no binary formats.
- **Invocation chain: GitHub Actions → Mise → uv.**
    The Actions workflow delegates entirely to Mise tasks.
    Developers can run `MISE_EXPERIMENTAL=1 mise run //github-analytics:ci` locally
    and exercise the exact same code path as CI.

## Architecture

Three components:

1. **Collector** (`github-analytics/`) in this monorepo.
   Reads `config.yaml` (repo allowlist), queries the GitHub API for 8 endpoint types,
   writes idempotent NDJSON files.
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
- `referrers.ndjson`: `{"collected_at": "...", "referrer": "...", "count": N, "uniques": N}`.
- `paths.ndjson`: `{"collected_at": "...", "path": "...", "title": "...", "count": N, "uniques": N}`.
- `stars.ndjson`: `{"starred_at": "...", "user": "..."}`.
- `forks.ndjson`: `{"forked_at": "...", "owner": "..."}`.
- `releases.ndjson`: `{"collected_at": "...", "tag": "...", "asset": "...", "download_count": N}`.
- `metadata.ndjson`: `{"date": "YYYY-MM-DD", "stars": N, "forks": N, "watchers": N, "open_issues": N}`.

Note: `watchers` always equals `stars` in GitHub's API since 2012.
Both are stored for completeness but should not be presented as distinct metrics in reports.

## Configuration

`github-analytics/config.yaml` contains only the repo allowlist.
Supported patterns: `org:<name>`, `user:<name>`, `<owner>/<repo>`.
All endpoints are always enabled.
Collection frequency is controlled by the GitHub Actions cron schedule.

## GitHub PAT Requirements

`ANALYTICS_DATA_PAT` must be a classic PAT (not fine-grained) with `repo` scope,
  created by the `karlmdavis` account.
The GitHub Traffic API requires push access to the queried repo,
  which cannot be expressed as a fine-grained permission across many repos.
The same PAT is used for pushing to the data repository.

## Error Handling

- Per-repo and per-endpoint failures are isolated: one failure does not stop others.
- Collector exits 1 if any error occurred; git operations still run to commit partial data.
- Rate limits: primary (429) and secondary (403 with `Retry-After`/`abuse`) are retried
    with exponential backoff, up to 3 attempts.
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

## References

- **Product Requirements**:
    [GitHub Analytics Collector](../product-requirements/2026-04-03-github-analytics-collector.md).
