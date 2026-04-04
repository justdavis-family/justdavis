---
title: GitHub Analytics Collector
status: draft
vision:
  - 2026-04-03-github-analytics
depends_on: []
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-04-03-github-analytics.md
prs: []
---

# GitHub Analytics Collector

## Summary

A daily-scheduled GitHub Actions workflow collects all available analytics metrics
  from the GitHub API for all configured repositories,
  appends the data as NDJSON to a dedicated data repository,
  and regenerates human-readable README reports at the root, per-owner, and per-repo levels.

## User Story

As Karl, I want all my GitHub repository analytics automatically collected daily
  and stored in a queryable, human-readable format
  so that I can track trends over time without manual effort
  and without losing data due to GitHub's 14-day traffic API retention window.

## Acceptance Criteria

### Data Collection

- [ ] All endpoints below are collected for every repo matching the configured allowlist.
- [ ] Data is stored as NDJSON in `justdavis-family/github-analytics-data`
        under `{owner}/{repo}/{metric}.ndjson`.
- [ ] Collection is idempotent: running twice on the same day produces no duplicate records.
- [ ] Per-repo failures do not prevent collection for other repos;
        the job still fails overall (triggering an email) if any repo fails.
- [ ] At least one integration test covers each endpoint type using VCR cassettes.
- [ ] The full `collect` + `report` pipeline is verified end-to-end by `test_e2e.py`
        against recorded cassettes.

#### Traffic Endpoints

- `GET /repos/{owner}/{repo}/traffic/views` — daily view and unique visitor counts.
- `GET /repos/{owner}/{repo}/traffic/clones` — daily clone and unique cloner counts.
- `GET /repos/{owner}/{repo}/traffic/popular/referrers` — top referral sources (snapshot).
- `GET /repos/{owner}/{repo}/traffic/popular/paths` — top paths by view count (snapshot).

#### Stats Endpoints

- `GET /repos/{owner}/{repo}/stats/commit_activity` — total commits per week for the last 52 weeks,
    with per-day-of-week breakdown.
- `GET /repos/{owner}/{repo}/stats/code_frequency` — weekly additions and deletions since repo creation.
- `GET /repos/{owner}/{repo}/stats/contributors` — per-contributor weekly commit, addition,
    and deletion counts.
- `GET /repos/{owner}/{repo}/stats/participation` — weekly commit counts (all contributors vs.
    repo owner only) for the last 52 weeks.
- `GET /repos/{owner}/{repo}/stats/punch_card` — commit counts by hour of day and day of week.

#### Other Endpoints

- `GET /repos/{owner}/{repo}` — point-in-time repo metadata snapshot: star count, fork count,
    watcher count, open issue count, network count, subscriber count, and repo size.
- `GET /repos/{owner}/{repo}/stargazers` — full star event history (user + timestamp).
- `GET /repos/{owner}/{repo}/forks` — full fork event history (owner + timestamp).
- `GET /repos/{owner}/{repo}/releases` — release asset download counts (snapshot per tag + asset).
- `GET /repos/{owner}/{repo}/actions/runs` — workflow run aggregates for the last 14 days,
    grouped by (date, workflow name, path, workflow id, status, conclusion);
    stores completed count, incomplete count, and average duration of completed runs.

### Reporting

The data repository's README files are regenerated after each collection run.
There are two README formats: one for multi-repo pages and one for single-repo pages.

#### Multi-Repo README Format

Used for the root-level README and each per-owner README.
Contents in order:

1. **Unique visitors stacked area chart** (SVG, pre-rendered via Vega-Lite):
    x-axis = date, y-axis = unique visitors per day, one stacked series per repo.
    Shows all available history.
2. **Unique clones stacked area chart** (SVG, Vega-Lite):
    same structure but y-axis = unique clones per day.
3. **Average daily traffic tables** — four separate tables (unique visitors, views,
    unique clones, clones); repos as rows, calendar quarters as columns;
    cell value = average daily count for that repo in that quarter.
4. **Current totals table**: one row per repo, columns for stars and forks
    (current values from the most recent metadata snapshot).
5. **Commits per week stacked area chart** (SVG, Vega-Lite):
    x-axis = week start date, y-axis = commits per week, one stacked series per repo.
    Shows all available history.
6. **Commits per week table**: repos as rows, calendar quarters as columns
    (covering the last 26 weeks only); cell value = total commits in that quarter
    within the 26-week window.

SVG chart files are written alongside each README (e.g. `unique_visitors.svg`)
  and referenced with relative `![alt](./chart.svg)` links.

#### Single-Repo README Format

Used for each per-repo README.
Contents in order (MermaidJS XY charts replace Vega-Lite SVGs):

1. **Unique visitors line chart** (MermaidJS `xychart-beta`): all available history.
2. **Unique clones line chart** (MermaidJS `xychart-beta`): all available history.
3. **Monthly traffic table**: one row per month, columns for unique visitors/day,
    views/day, unique clones/day, and clones/day (average daily counts per month).
4. **Current totals table** (pivoted): rows for stars and forks,
    single value column (more readable with only one repo).
5. **Commits per week line chart** (MermaidJS `xychart-beta`): all available history.
6. **Commits per week table**: one row per week (last 26 weeks), single commits column.

## References

### Vision

- [GitHub Analytics Data Collection](../product-vision/2026-04-03-github-analytics.md) —
    Durable, queryable capture of GitHub metrics to prevent data loss
    from the 14-day API retention window.

### Engineering Design

- [GitHub Analytics Engineering Design](../engineering-designs/2026-04-03-github-analytics.md) —
    Python package with uv tooling, NDJSON storage, VCR-based tests,
    and GitHub Actions → Mise → uv invocation chain.

### Related Requirements

- None.

### Implementation

- None yet.
