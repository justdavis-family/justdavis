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

- [ ] All endpoints are collected for every repo matching the configured allowlist:
        traffic views, traffic clones, referrer snapshots, popular path snapshots,
        star events, fork events, release download counts, and repository metadata.
- [ ] Data is stored as NDJSON in `justdavis-family/github-analytics-data`
        under `{owner}/{repo}/{metric}.ndjson`.
- [ ] Collection is idempotent: running twice on the same day produces no duplicate records.
- [ ] Per-repo failures do not prevent collection for other repos;
        the job still fails overall (triggering an email) if any repo fails.
- [ ] The data repository's README files are regenerated after each collection run,
        presenting stats grouped by metric type at the root level,
        and full per-repo detail (monthly table + Mermaid line chart) at the repo level.
- [ ] At least one integration test covers each endpoint type using VCR cassettes.
- [ ] The full `collect` + `report` pipeline is verified end-to-end by `test_e2e.py`
        against recorded cassettes.

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
