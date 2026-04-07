---
title: GitHub Analytics Interactive Reporter (GitHub Pages)
status: draft
vision:
  - 2026-04-03-github-analytics
depends_on:
  - 2026-04-03-github-analytics-collector
extends:
  - 2026-04-03-github-analytics-collector
modifies: []
replaces: []
engineering_designs: []
prs: []
---

# GitHub Analytics Interactive Reporter (GitHub Pages)

## Summary

A GitHub Pages site generated from the collected NDJSON data
  provides an interactive alternative to the current static Markdown READMEs.
The Markdown reporter's UX is fundamentally constrained by GitHub's rendering pipeline:
  charts are small, non-interactive SVG or Mermaid images with no series labels or hover state;
  tables cannot be sorted or filtered;
  column limits force quarterly aggregation that discards the finer granularity available in the data.
A GitHub Pages reporter lifts all of these constraints,
  enabling interactive exploration and comparison across the full dataset.

## User Story

As Karl, I want my collected GitHub analytics rendered as an interactive GitHub Pages site
  so that I can explore traffic trends, sort and filter across all repos simultaneously,
  and see data at the granularity I choose —
  rather than being limited by what GitHub's Markdown renderer can display.

## Acceptance Criteria

### Charts

- [ ] All multi-repo and per-repo charts are rendered as interactive HTML+JavaScript
        (not static SVGs or Mermaid diagrams).
- [ ] Hovering over any data point reveals its exact value, date, and series label.
- [ ] Multi-series charts (e.g. stacked area charts with one series per repo)
        clearly label each series and support toggling individual series on/off.
- [ ] Charts support time-range selection (e.g. a draggable date slider or click-to-zoom)
        so the user can zoom into a period of interest without leaving the page.
- [ ] Charts are responsive to viewport width.

### Tables

- [ ] All traffic tables are sortable by clicking any column header.
- [ ] Tables support a text filter that narrows rows by repository name substring.
- [ ] Applying a filter or sort on one table applies it to all tables on the same page,
        so repos can be directly compared across metrics without repeated manual filtering.
- [ ] Time series granularity is user-configurable via a toggle on each page
        (Day / Week / Month / Quarter / Year),
        defaulting to a granularity that shows the full available history without truncation.
- [ ] At the finest available granularity (Day), daily values are shown directly
        rather than averaged — the current quarterly averaging discards useful signal.
- [ ] Release download tables support sorting by tag, asset name, and download count.

### Site Structure and Deployment

- [ ] The GitHub Pages site mirrors the three-level structure of the existing Markdown reports:
        a root index, per-owner pages, and per-repo pages.
- [ ] GitHub Pages generation is a new `pages` subcommand (or a flag on `report`)
        that reads the same NDJSON files as the Markdown reporter.
- [ ] The existing Markdown READMEs are preserved alongside the Pages site
        so the data repo remains browsable via GitHub's native UI.
- [ ] The GitHub Pages site is published from the data repository
        (e.g. via a `gh-pages` branch or the `docs/` folder),
        not from this tool repository.
- [ ] The collection workflow is updated to run `pages` after `report`
        and commit the generated site files alongside the NDJSON data.

### Testing

- [ ] At least one integration test verifies that the Pages generator
        produces valid HTML output for a representative NDJSON fixture.
- [ ] The end-to-end test in `test_e2e.py` is extended to verify
        the `pages` subcommand runs without error and produces expected output files.

## References

### Vision

- [GitHub Analytics Data Collection](../product-vision/2026-04-03-github-analytics.md) —
    Durable, queryable capture of GitHub metrics to prevent data loss
    from the 14-day API retention window.
    This requirement addresses the presentation layer of that vision.

### Engineering Design

- None yet.

### Related Requirements

- [GitHub Analytics Collector](2026-04-03-github-analytics-collector.md) —
    Provides the NDJSON data files that the Pages reporter reads;
    this requirement extends its reporting capability.

### Implementation

- None yet.
