# GitHub Analytics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
>   (recommended) or superpowers:executing-plans to implement this plan task-by-task.
>   Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a daily GitHub Analytics collector that durably captures all-available API metrics
  for all tracked repos, stores them as queryable NDJSON in a dedicated data repository,
  and generates human-readable README reports — running entirely on GitHub Actions with no
  home-lab dependencies.

**Architecture:** A Python package (`github-analytics/`) in this monorepo reads a repo allowlist,
  calls the GitHub API for 8 endpoint types per repo, and writes idempotent NDJSON files to a local
  checkout of `justdavis-family/github-analytics-data`.
A reporter generates three levels of Markdown README (root, per-owner, per-repo).
A scheduled GitHub Actions workflow orchestrates everything: checkout → collect → report → git push.

**Tech Stack:** Python 3.12, uv, httpx, PyYAML, ruff, mypy (strict), pytest, pytest-recording (vcrpy).
  Invocation chain: GitHub Actions → Mise → uv.

---

## File Map

Files to be created or modified, by module:

### Design artifacts
- Create: `design/product-vision/2026-04-03-github-analytics.md`
- Create: `design/product-requirements/2026-04-03-github-analytics-collector.md`
- Create: `design/engineering-designs/2026-04-03-github-analytics.md`
- Modify: `design/engineering-principles/2026-01-06-yagni.md`

### Package scaffold
- Create: `github-analytics/pyproject.toml`
- Create: `github-analytics/mise.toml`
- Create: `github-analytics/config.yaml`
- Create: `github-analytics/github_analytics/__init__.py`
- Modify: `mise.toml` (root)

### Config module
- Create: `github-analytics/github_analytics/config.py`
- Create: `github-analytics/tests/__init__.py`
- Create: `github-analytics/tests/test_config.py`
- Create: `github-analytics/tests/cassettes/` (VCR cassette YAML files)

### Writer module
- Create: `github-analytics/github_analytics/writer.py`
- Create: `github-analytics/tests/test_writer.py`

### Fetcher module
- Create: `github-analytics/github_analytics/fetcher.py`
- Create: `github-analytics/tests/test_fetcher.py`

### CLI and E2E tests
- Create: `github-analytics/github_analytics/__main__.py`
- Create: `github-analytics/tests/test_e2e.py`

### Reporter module
- Create: `github-analytics/github_analytics/reporter.py`

### GitHub Actions workflow
- Create: `.github/workflows/github-analytics.yml`

---

## Task 1: Write Design Artifacts

**Files:**
- Create: `design/product-vision/2026-04-03-github-analytics.md`
- Create: `design/product-requirements/2026-04-03-github-analytics-collector.md`
- Create: `design/engineering-designs/2026-04-03-github-analytics.md`
- Modify: `design/engineering-principles/2026-01-06-yagni.md`

Templates are at `design/product-vision/template.md`,
  `design/product-requirements/template.md`, and
  `design/engineering-designs/template.md`.
Follow the markdown style rules in `.claude/rules/markdown-style.md`:
  one sentence per line, 110-char wrap, POSIX line endings.

- [ ] **Step 1: Write product vision**

  Create `design/product-vision/2026-04-03-github-analytics.md`:

  ```markdown
  # GitHub Analytics Data Collection

  ## Problem and Motivation

  GitHub's Traffic API retains only 14 days of analytics data.
  Without proactive collection, traffic history is permanently lost.
  Karl has no durable record of how his repositories are used over time,
    making it impossible to track trends, measure impact, or debug traffic anomalies.

  ## Vision

  A lightweight, zero-maintenance analytics collection system
    that captures all available GitHub metrics daily,
    stores them in a durable and queryable format,
    and presents them as human-readable reports directly on GitHub.
  The system runs entirely on GitHub-managed infrastructure,
    requires no home lab or external services,
    and surfaces failures immediately via GitHub's built-in email notifications.

  ## Success Metrics

  - No traffic data gaps for any tracked repository after initial deployment.
  - Collection failures are surfaced via email within 24 hours.
  - Any tracked repository's analytics history is queryable with standard CLI tools
      (`jq`, `grep`) on macOS and Linux without additional tooling.
  - Visiting `github.com/justdavis-family/github-analytics-data` shows
      a formatted summary of all tracked repositories without requiring any local tooling.

  ## Requirements

  This vision is being implemented through the following requirements:

  - [GitHub Analytics Collector](../product-requirements/2026-04-03-github-analytics-collector.md) —
      Daily collection and reporting of all available GitHub analytics metrics (in progress).
  ```

- [ ] **Step 2: Write product requirement**

  Create `design/product-requirements/2026-04-03-github-analytics-collector.md`:

  ```markdown
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
  ```

- [ ] **Step 3: Write engineering design**

  Create `design/engineering-designs/2026-04-03-github-analytics.md`:

  ```markdown
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

  Repository: `justdavis-family/github-analytics-data`

  Directory structure: `{owner}/{repo}/{metric}.ndjson`

  NDJSON formats (one JSON object per line, all timestamps ISO 8601 UTC):

  - `views.ndjson` / `clones.ndjson`: `{"date": "YYYY-MM-DD", "count": N, "uniques": N}`
  - `referrers.ndjson`: `{"collected_at": "...", "referrer": "...", "count": N, "uniques": N}`
  - `paths.ndjson`: `{"collected_at": "...", "path": "...", "title": "...", "count": N, "uniques": N}`
  - `stars.ndjson`: `{"starred_at": "...", "user": "..."}`
  - `forks.ndjson`: `{"forked_at": "...", "owner": "..."}`
  - `releases.ndjson`: `{"collected_at": "...", "tag": "...", "asset": "...", "download_count": N}`
  - `metadata.ndjson`: `{"date": "YYYY-MM-DD", "stars": N, "forks": N, "watchers": N, "open_issues": N}`

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
  ```

- [ ] **Step 4: Update YAGNI principle**

  Edit `design/engineering-principles/2026-01-06-yagni.md`.
  Add a new subsection to the "Examples" section documenting "minimal configuration" as a named
  application of YAGNI.
  Insert before the `## When to Break This Rule` heading:

  ```markdown
  ### Application: Minimal Configuration

  A common YAGNI violation is offering configuration options for things that have only one
    proven use case.
  Before adding a configuration option, ask: is there a real, current need for this to vary?

  **Good:** A data collector with a fixed set of endpoints — all endpoints are always collected.
    If the need to disable specific endpoints arises later, add it then.

  **Bad:** Adding an `endpoints:` block to a config file "in case someone wants to disable
    traffic collection" when there is no current use case for disabling it.
  ```

- [ ] **Step 5: Commit design artifacts**

  ```bash
  git add design/product-vision/2026-04-03-github-analytics.md \
          design/product-requirements/2026-04-03-github-analytics-collector.md \
          design/engineering-designs/2026-04-03-github-analytics.md \
          design/engineering-principles/2026-01-06-yagni.md
  git commit -m "design: add github analytics product vision, requirements, and engineering design"
  ```

---

## Task 2: Python Package Scaffold

**Files:**
- Create: `github-analytics/pyproject.toml`
- Create: `github-analytics/mise.toml`
- Create: `github-analytics/config.yaml`
- Create: `github-analytics/github_analytics/__init__.py`
- Create: `github-analytics/tests/__init__.py`
- Modify: `mise.toml` (root)

- [ ] **Step 1: Create pyproject.toml**

  Create `github-analytics/pyproject.toml`:

  ```toml
  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build"

  [project]
  name = "github-analytics"
  version = "0.1.0"
  requires-python = ">=3.12"
  dependencies = [
      "httpx>=0.27",
      "pyyaml>=6.0",
  ]

  [dependency-groups]
  dev = [
      "mypy>=1.11",
      "pytest>=8.0",
      "pytest-recording>=0.13",
      "ruff>=0.6",
      "types-PyYAML>=6.0",
  ]

  [tool.ruff]
  line-length = 110

  [tool.ruff.lint]
  select = ["E", "F", "I", "UP", "ANN"]

  [tool.mypy]
  strict = true

  [tool.pytest.ini_options]
  testpaths = ["tests"]
  ```

- [ ] **Step 2: Create mise.toml**

  Create `github-analytics/mise.toml`:

  ```toml
  [tools]
  python = "3.12"
  uv = "latest"

  [tasks.build]
  description = "Sync dependencies via uv"
  run = "uv sync --all-groups"

  [tasks.test]
  description = "Run tests"
  depends = ["build"]
  run = "uv run pytest"

  [tasks.lint]
  description = "Lint and format check"
  depends = ["build"]
  run = [
    "uv run ruff check .",
    "uv run ruff format --check .",
  ]

  [tasks.typecheck]
  description = "Type check"
  depends = ["build"]
  run = "uv run mypy github_analytics/"

  [tasks.ci]
  description = "Full CI suite"
  depends = ["test", "lint", "typecheck"]

  [tasks."dependencies:check"]
  description = "Check for outdated or vulnerable dependencies"
  depends = ["build"]
  run = "uv tree --outdated"

  [tasks."dependencies:update"]
  description = "Update dependencies to latest compatible versions"
  run = "uv lock --upgrade && uv sync --all-groups"

  [tasks.collect]
  description = "Collect GitHub analytics (pass --data-repo PATH as trailing args)"
  depends = ["build"]
  run = "uv run python -m github_analytics collect"

  [tasks.report]
  description = "Generate analytics README reports (pass --data-repo PATH as trailing args)"
  depends = ["build"]
  run = "uv run python -m github_analytics report"

  [tasks."collect:smoke"]
  description = "Smoke test: collect against live GitHub API into /tmp/"
  depends = ["build"]
  run = "uv run python -m github_analytics collect --data-repo /tmp/analytics-smoke-$(date +%s)"
  ```

- [ ] **Step 3: Create config.yaml**

  Create `github-analytics/config.yaml`:

  ```yaml
  # Repositories to track. Supported patterns:
  #   org:<orgname>    - all public repos in an org
  #   user:<username>  - all public repos for a user
  #   <owner>/<repo>   - a specific repo
  repos:
    - "org:justdavis-family"
    - "user:karlmdavis"
  ```

- [ ] **Step 4: Create package init files**

  Create `github-analytics/github_analytics/__init__.py` (empty).
  Create `github-analytics/tests/__init__.py` (empty).

- [ ] **Step 5: Update root mise.toml**

  In the root `mise.toml`, update:
  - `config_roots`: replace `"*"` with `"github-analytics"` (or add it to the list when more exist).
  - Add `"//github-analytics:build"` to `[tasks.build]` depends.
  - Add `"//github-analytics:lint"` to `[tasks."lint:all"]` depends.
  - Add `"//github-analytics:test"` to `[tasks."test:all"]` depends.

  Resulting root `mise.toml`:

  ```toml
  experimental_monorepo_root = true

  [monorepo]
  config_roots = [
    "github-analytics",
  ]

  [tools]
  yq = "latest"

  [tasks.build]
  description = "Build all projects"
  depends = ["//github-analytics:build"]

  [tasks."lint:all"]
  description = "Lint all projects"
  depends = ["//github-analytics:lint", "//github-analytics:typecheck"]

  [tasks."test:all"]
  description = "Test all projects"
  depends = ["//github-analytics:test"]

  [tasks.ci]
  description = "Run full CI suite"
  depends = ["build", "test:all", "lint:all"]

  [tasks."ci:github:watch"]
  description = "Watch GitHub PR checks"
  run = "gh pr checks --watch --fail-fast"

  [tasks."install:hooks"]
  description = "Install git hooks"
  run = "git config core.hooksPath .githooks && chmod +x .githooks/*"
  ```

- [ ] **Step 6: Install dependencies and generate lockfile**

  ```bash
  cd github-analytics
  MISE_EXPERIMENTAL=1 mise run :build
  ```

  This creates `github-analytics/uv.lock`.

- [ ] **Step 7: Verify scaffold compiles**

  ```bash
  MISE_EXPERIMENTAL=1 mise run //github-analytics:ci
  ```

  Expected: passes (no source files to lint/test yet, but the setup should not error).
  If tests fail because there are no tests, add `--ignore=tests/` temporarily
  or create a placeholder `tests/test_placeholder.py` with a single `pass`.

- [ ] **Step 8: Commit scaffold**

  ```bash
  git add github-analytics/ mise.toml
  git commit -m "feat(github-analytics): add python package scaffold with uv, ruff, mypy"
  ```

---

## Task 3: Record VCR Cassettes

VCR cassettes capture real GitHub API responses and replay them in tests without network access.
They must be recorded before writing cassette-dependent tests.

**Files:**
- Create: `github-analytics/tests/cassettes/` (auto-generated YAML files)
- Create: `github-analytics/tests/conftest.py`

**Prerequisites:** `GITHUB_TOKEN` environment variable set with a PAT that has push access
  to `karlmdavis/ksoap2-android` (for realistic traffic data).

- [ ] **Step 1: Create conftest.py**

  Create `github-analytics/tests/conftest.py`:

  ```python
  import pytest


  @pytest.fixture(scope="session")
  def vcr_config() -> dict[str, object]:
      """VCR configuration: store cassettes in tests/cassettes/, filter auth headers.

      Must be session-scoped so pytest-recording applies this config globally.
      """
      return {
          "cassette_library_dir": "tests/cassettes",
          "filter_headers": ["authorization"],
          "record_mode": "none",  # Fail if cassette missing; use --record-mode=new_episodes to record
      }
  ```

- [ ] **Step 2: Write the cassette-recording test file**

  Create `github-analytics/tests/recording_tests.py`
  (a pytest file that records cassettes when run with `--record-mode=new_episodes`;
  ONLY for recording — not run in normal CI since it requires a live GITHUB_TOKEN).

  Also update `pyproject.toml` `[tool.pytest.ini_options]` to exclude it from default runs:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  addopts = "--ignore=tests/recording_tests.py"
  ```

  Create `github-analytics/tests/recording_tests.py`:

  ```python
  """Run with --record-mode=new_episodes and GITHUB_TOKEN set to record VCR cassettes.

  Usage:
      cd github-analytics
      GITHUB_TOKEN=ghp_... uv run pytest tests/recording_tests.py \\
        --record-mode=new_episodes -v

  pytest-recording intercepts httpx calls and writes cassettes to tests/cassettes/.
  The authorization header is filtered from all cassettes (see conftest.py vcr_config).
  """
  import os
  import pytest
  from github_analytics import fetcher
  from github_analytics.config import RepoId, _list_org_repos, _list_user_repos

  KSOAP = RepoId(owner="karlmdavis", name="ksoap2-android")
  JUSTDAVIS = RepoId(owner="justdavis-family", name="justdavis")


  def _token() -> str:
      return os.environ["GITHUB_TOKEN"]


  @pytest.mark.vcr("traffic_views.yaml")
  def test_record_traffic_views() -> None:
      fetcher.fetch_traffic_views(KSOAP, _token())


  @pytest.mark.vcr("traffic_clones.yaml")
  def test_record_traffic_clones() -> None:
      fetcher.fetch_traffic_clones(KSOAP, _token())


  @pytest.mark.vcr("traffic_referrers.yaml")
  def test_record_traffic_referrers() -> None:
      fetcher.fetch_traffic_referrers(KSOAP, _token())


  @pytest.mark.vcr("traffic_paths.yaml")
  def test_record_traffic_paths() -> None:
      fetcher.fetch_traffic_paths(KSOAP, _token())


  @pytest.mark.vcr("stars.yaml")
  def test_record_stars() -> None:
      fetcher.fetch_stars(KSOAP, _token())


  @pytest.mark.vcr("forks.yaml")
  def test_record_forks() -> None:
      fetcher.fetch_forks(KSOAP, _token())


  @pytest.mark.vcr("releases.yaml")
  def test_record_releases() -> None:
      fetcher.fetch_releases(KSOAP, _token())


  @pytest.mark.vcr("metadata.yaml")
  def test_record_metadata() -> None:
      fetcher.fetch_metadata(KSOAP, _token())


  @pytest.mark.vcr("traffic_views_quiet.yaml")
  def test_record_traffic_views_quiet() -> None:
      fetcher.fetch_traffic_views(JUSTDAVIS, _token())


  @pytest.mark.vcr("metadata_quiet.yaml")
  def test_record_metadata_quiet() -> None:
      fetcher.fetch_metadata(JUSTDAVIS, _token())


  @pytest.mark.vcr("org_repos.yaml")
  def test_record_org_repos() -> None:
      _list_org_repos("justdavis-family", _token())


  @pytest.mark.vcr("user_repos.yaml")
  def test_record_user_repos() -> None:
      _list_user_repos("karlmdavis", _token())
  ```

- [ ] **Step 3: Record cassettes**

  Ensure `GITHUB_TOKEN` is set (PAT with push access to `karlmdavis/ksoap2-android`):

  ```bash
  cd github-analytics
  GITHUB_TOKEN=<your-pat> uv run pytest tests/recording_tests.py \
    --record-mode=new_episodes -v
  ```

  Expected: 12 YAML cassette files created in `tests/cassettes/`.
  Verify: `ls tests/cassettes/` shows the 12 files listed above.

- [ ] **Step 4: Commit cassettes**

  ```bash
  git add github-analytics/tests/
  git commit -m "test(github-analytics): add VCR cassettes for all GitHub API endpoints"
  ```

---

## Task 4: Config Module (TDD)

**Files:**
- Create: `github-analytics/github_analytics/config.py`
- Create: `github-analytics/tests/test_config.py`

The config module parses `config.yaml` and expands `org:` and `user:` patterns by calling the
  GitHub API to list repositories.

- [ ] **Step 1: Write failing tests**

  Create `github-analytics/tests/test_config.py`:

  ```python
  import pytest
  from pathlib import Path
  from github_analytics.config import load_repos, RepoId


  def test_load_repos_explicit(tmp_path: Path) -> None:
      """Explicit owner/repo entries are returned as-is."""
      config = tmp_path / "config.yaml"
      config.write_text("repos:\n  - karlmdavis/ksoap2-android\n  - justdavis-family/justdavis\n")
      result = load_repos(config, token="unused")
      assert result == [
          RepoId(owner="karlmdavis", name="ksoap2-android"),
          RepoId(owner="justdavis-family", name="justdavis"),
      ]


  @pytest.mark.vcr("org_repos.yaml")
  def test_load_repos_org_wildcard(tmp_path: Path) -> None:
      """org: entries are expanded to all repos in the org."""
      config = tmp_path / "config.yaml"
      config.write_text("repos:\n  - org:justdavis-family\n")
      result = load_repos(config, token="fake-token")
      # justdavis-family has at least the justdavis repo
      assert any(r["owner"] == "justdavis-family" for r in result)


  @pytest.mark.vcr("user_repos.yaml")
  def test_load_repos_user_wildcard(tmp_path: Path) -> None:
      """user: entries are expanded to all repos for the user."""
      config = tmp_path / "config.yaml"
      config.write_text("repos:\n  - user:karlmdavis\n")
      result = load_repos(config, token="fake-token")
      assert any(r["owner"] == "karlmdavis" for r in result)


  def test_load_repos_deduplication(tmp_path: Path) -> None:
      """A repo appearing via wildcard and explicit entry is returned once."""
      config = tmp_path / "config.yaml"
      config.write_text(
          "repos:\n  - justdavis-family/justdavis\n  - justdavis-family/justdavis\n"
      )
      result = load_repos(config, token="unused")
      assert result.count(RepoId(owner="justdavis-family", name="justdavis")) == 1
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  cd github-analytics && uv run pytest tests/test_config.py -v
  ```

  Expected: `ModuleNotFoundError: No module named 'github_analytics.config'`

- [ ] **Step 3: Implement config.py**

  Create `github-analytics/github_analytics/config.py`:

  ```python
  """Config loading: parse config.yaml and expand repo patterns."""
  from __future__ import annotations

  from pathlib import Path
  from typing import TypedDict

  import httpx
  import yaml


  class RepoId(TypedDict):
      """Identifies a GitHub repository."""
      owner: str
      name: str


  def load_repos(config_path: Path, token: str) -> list[RepoId]:
      """Load and expand the repository list from config.yaml.

      Expands ``org:<name>`` and ``user:<name>`` patterns via the GitHub API.
      Deduplicates the result.
      """
      with config_path.open() as f:
          raw: dict[str, list[str]] = yaml.safe_load(f)

      patterns: list[str] = raw.get("repos", [])
      repos: list[RepoId] = []
      seen: set[tuple[str, str]] = set()

      for pattern in patterns:
          for repo in _expand_pattern(pattern, token):
              key = (repo["owner"], repo["name"])
              if key not in seen:
                  seen.add(key)
                  repos.append(repo)
      return repos


  def _expand_pattern(pattern: str, token: str) -> list[RepoId]:
      """Expand a single pattern to a list of RepoIds."""
      if pattern.startswith("org:"):
          org = pattern[4:]
          return _list_org_repos(org, token)
      if pattern.startswith("user:"):
          user = pattern[5:]
          return _list_user_repos(user, token)
      # Explicit owner/repo
      owner, name = pattern.split("/", 1)
      return [RepoId(owner=owner, name=name)]


  def _list_org_repos(org: str, token: str) -> list[RepoId]:
      return _paginate(f"https://api.github.com/orgs/{org}/repos", token)


  def _list_user_repos(user: str, token: str) -> list[RepoId]:
      return _paginate(f"https://api.github.com/users/{user}/repos", token)


  def _paginate(url: str, token: str) -> list[RepoId]:
      headers = {
          "Authorization": f"token {token}",
          "Accept": "application/vnd.github+json",
      }
      repos: list[RepoId] = []
      next_url: str | None = url
      while next_url:
          response = httpx.get(next_url, headers=headers, follow_redirects=True)
          response.raise_for_status()
          for item in response.json():
              repos.append(RepoId(owner=item["owner"]["login"], name=item["name"]))
          next_url = _next_link(response.headers.get("link", ""))
      return repos


  def _next_link(link_header: str) -> str | None:
      """Parse GitHub's Link header and return the 'next' URL, if any."""
      for part in link_header.split(","):
          url_part, *params = part.strip().split(";")
          if any('rel="next"' in p for p in params):
              return url_part.strip().strip("<>")
      return None
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  cd github-analytics && uv run pytest tests/test_config.py -v
  ```

  Expected: all 4 tests pass.

- [ ] **Step 5: Run lint and typecheck**

  ```bash
  cd github-analytics && uv run ruff check . && uv run mypy github_analytics/
  ```

  Expected: no errors.

- [ ] **Step 6: Commit**

  ```bash
  git add github-analytics/github_analytics/config.py github-analytics/tests/test_config.py \
          github-analytics/tests/conftest.py github-analytics/tests/record_cassettes.py
  git commit -m "feat(github-analytics): implement config module with repo allowlist expansion"
  ```

---

## Task 5: Writer Module (TDD)

**Files:**
- Create: `github-analytics/github_analytics/writer.py`
- Create: `github-analytics/tests/test_writer.py`

The writer appends NDJSON records idempotently using atomic file writes.

- [ ] **Step 1: Write failing tests**

  Create `github-analytics/tests/test_writer.py`:

  ```python
  import json
  from pathlib import Path
  from github_analytics.writer import append_record


  def test_append_record_creates_file(tmp_path: Path) -> None:
      """append_record creates the file and parent dirs if they don't exist."""
      dest = tmp_path / "owner" / "repo" / "views.ndjson"
      record = {"date": "2026-04-03", "count": 10, "uniques": 5}
      appended = append_record(dest, record, key_fields=["date"])
      assert appended is True
      assert dest.exists()
      lines = dest.read_text().strip().splitlines()
      assert len(lines) == 1
      assert json.loads(lines[0]) == record


  def test_append_record_appends_new_record(tmp_path: Path) -> None:
      """New records with different keys are appended."""
      dest = tmp_path / "views.ndjson"
      r1 = {"date": "2026-04-03", "count": 10, "uniques": 5}
      r2 = {"date": "2026-04-04", "count": 12, "uniques": 6}
      append_record(dest, r1, key_fields=["date"])
      appended = append_record(dest, r2, key_fields=["date"])
      assert appended is True
      lines = dest.read_text().strip().splitlines()
      assert len(lines) == 2


  def test_append_record_deduplicates(tmp_path: Path) -> None:
      """A record with the same key is not appended again."""
      dest = tmp_path / "views.ndjson"
      record = {"date": "2026-04-03", "count": 10, "uniques": 5}
      append_record(dest, record, key_fields=["date"])
      appended = append_record(dest, record, key_fields=["date"])
      assert appended is False
      lines = dest.read_text().strip().splitlines()
      assert len(lines) == 1


  def test_append_record_composite_key(tmp_path: Path) -> None:
      """Composite keys are checked correctly."""
      dest = tmp_path / "stars.ndjson"
      r1 = {"starred_at": "2025-01-01T00:00:00Z", "user": "alice"}
      r2 = {"starred_at": "2025-01-01T00:00:00Z", "user": "bob"}
      r_dup = {"starred_at": "2025-01-01T00:00:00Z", "user": "alice"}
      append_record(dest, r1, key_fields=["starred_at", "user"])
      append_record(dest, r2, key_fields=["starred_at", "user"])
      appended = append_record(dest, r_dup, key_fields=["starred_at", "user"])
      assert appended is False
      assert len(dest.read_text().strip().splitlines()) == 2


  def test_append_record_atomic_write(tmp_path: Path) -> None:
      """File contents are not corrupted if process crashes mid-write.
      We test this by verifying the final file has valid JSON on every line."""
      dest = tmp_path / "views.ndjson"
      for i in range(5):
          append_record(dest, {"date": f"2026-04-0{i+1}", "count": i, "uniques": i}, key_fields=["date"])
      for line in dest.read_text().strip().splitlines():
          json.loads(line)  # raises if malformed
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  cd github-analytics && uv run pytest tests/test_writer.py -v
  ```

  Expected: `ModuleNotFoundError: No module named 'github_analytics.writer'`

- [ ] **Step 3: Implement writer.py**

  Create `github-analytics/github_analytics/writer.py`:

  ```python
  """NDJSON writer with idempotent append and atomic file writes."""
  from __future__ import annotations

  import json
  import os
  import tempfile
  from pathlib import Path
  from typing import Any


  def append_record(
      file_path: Path,
      record: dict[str, Any],
      key_fields: list[str],
  ) -> bool:
      """Append ``record`` to ``file_path`` if no existing record matches on ``key_fields``.

      Creates the file (and parent directories) if they don't exist.
      Uses atomic temp-file-then-rename to avoid partial writes.

      Returns:
          True if the record was appended, False if it was already present.
      """
      file_path.parent.mkdir(parents=True, exist_ok=True)

      record_key = tuple(record[f] for f in key_fields)

      # Check for existing record with the same key
      if file_path.exists():
          for line in file_path.read_text().splitlines():
              line = line.strip()
              if not line:
                  continue
              existing = json.loads(line)
              if tuple(existing.get(f) for f in key_fields) == record_key:
                  return False

      # Atomic append: read existing content, append new line, write via rename
      existing_content = file_path.read_text() if file_path.exists() else ""
      new_content = existing_content + json.dumps(record, separators=(",", ":")) + "\n"

      dir_path = file_path.parent
      fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
      try:
          with os.fdopen(fd, "w") as f:
              f.write(new_content)
          os.replace(tmp_path, file_path)
      except Exception:
          try:
              os.unlink(tmp_path)
          except OSError:
              pass
          raise
      return True
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  cd github-analytics && uv run pytest tests/test_writer.py -v
  ```

  Expected: all 5 tests pass.

- [ ] **Step 5: Run lint and typecheck**

  ```bash
  cd github-analytics && uv run ruff check . && uv run mypy github_analytics/
  ```

- [ ] **Step 6: Commit**

  ```bash
  git add github-analytics/github_analytics/writer.py github-analytics/tests/test_writer.py
  git commit -m "feat(github-analytics): implement idempotent NDJSON writer with atomic writes"
  ```

---

## Task 6: Fetcher Module (TDD)

**Files:**
- Create: `github-analytics/github_analytics/fetcher.py`
- Create: `github-analytics/tests/test_fetcher.py`

The fetcher calls GitHub API endpoints and returns typed records.
Tests use VCR cassettes recorded in Task 3.

- [ ] **Step 1: Write failing tests**

  Create `github-analytics/tests/test_fetcher.py`:

  ```python
  import pytest
  from github_analytics.fetcher import (
      fetch_traffic_views,
      fetch_traffic_clones,
      fetch_traffic_referrers,
      fetch_traffic_paths,
      fetch_stars,
      fetch_forks,
      fetch_releases,
      fetch_metadata,
  )
  from github_analytics.config import RepoId

  TOKEN = "fake-token"
  KSOAP = RepoId(owner="karlmdavis", name="ksoap2-android")


  @pytest.mark.vcr("traffic_views.yaml")
  def test_fetch_traffic_views_returns_records() -> None:
      records = fetch_traffic_views(KSOAP, TOKEN)
      assert isinstance(records, list)
      if records:
          r = records[0]
          assert "date" in r
          assert "count" in r
          assert "uniques" in r


  @pytest.mark.vcr("traffic_clones.yaml")
  def test_fetch_traffic_clones_returns_records() -> None:
      records = fetch_traffic_clones(KSOAP, TOKEN)
      assert isinstance(records, list)


  @pytest.mark.vcr("traffic_referrers.yaml")
  def test_fetch_traffic_referrers_returns_records() -> None:
      records = fetch_traffic_referrers(KSOAP, TOKEN)
      assert isinstance(records, list)
      if records:
          r = records[0]
          assert "collected_at" in r
          assert "referrer" in r
          assert "count" in r
          assert "uniques" in r


  @pytest.mark.vcr("traffic_paths.yaml")
  def test_fetch_traffic_paths_returns_records() -> None:
      records = fetch_traffic_paths(KSOAP, TOKEN)
      assert isinstance(records, list)


  @pytest.mark.vcr("stars.yaml")
  def test_fetch_stars_returns_records() -> None:
      records = fetch_stars(KSOAP, TOKEN)
      assert isinstance(records, list)
      if records:
          r = records[0]
          assert "starred_at" in r
          assert "user" in r


  @pytest.mark.vcr("forks.yaml")
  def test_fetch_forks_returns_records() -> None:
      records = fetch_forks(KSOAP, TOKEN)
      assert isinstance(records, list)
      if records:
          r = records[0]
          assert "forked_at" in r
          assert "owner" in r


  @pytest.mark.vcr("releases.yaml")
  def test_fetch_releases_returns_records() -> None:
      records = fetch_releases(KSOAP, TOKEN)
      assert isinstance(records, list)


  @pytest.mark.vcr("metadata.yaml")
  def test_fetch_metadata_returns_record() -> None:
      record = fetch_metadata(KSOAP, TOKEN)
      assert "date" in record
      assert "stars" in record
      assert "forks" in record
      assert "watchers" in record
      assert "open_issues" in record
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  cd github-analytics && uv run pytest tests/test_fetcher.py -v
  ```

  Expected: `ModuleNotFoundError: No module named 'github_analytics.fetcher'`

- [ ] **Step 3: Implement fetcher.py**

  Create `github-analytics/github_analytics/fetcher.py`:

  ```python
  """GitHub API fetcher for all analytics endpoints."""
  from __future__ import annotations

  import time
  from datetime import UTC, datetime
  from typing import Any

  import httpx

  from github_analytics.config import RepoId

  BASE = "https://api.github.com"
  _MAX_RETRIES = 3


  def _headers(token: str, accept: str = "application/vnd.github+json") -> dict[str, str]:
      return {"Authorization": f"token {token}", "Accept": accept}


  def _get_with_retry(url: str, headers: dict[str, str]) -> httpx.Response:
      """HTTP GET with retry for primary (429) and secondary (403 abuse) rate limits."""
      last_response: httpx.Response | None = None
      for attempt in range(_MAX_RETRIES):
          response = httpx.get(url, headers=headers, follow_redirects=True)
          last_response = response
          if response.status_code == 429:
              wait = float(response.headers.get("retry-after", 2 ** attempt))
              time.sleep(wait)
              continue
          if response.status_code == 403:
              body = response.text.lower()
              retry_after = response.headers.get("retry-after")
              if retry_after or "abuse" in body or "secondary rate" in body:
                  wait = float(retry_after or 2 ** attempt)
                  time.sleep(wait)
                  continue
          return response
      assert last_response is not None
      return last_response


  def _get(url: str, token: str, accept: str = "application/vnd.github+json") -> Any:
      """GET a single URL, raise on HTTP error, return parsed JSON."""
      response = _get_with_retry(url, _headers(token, accept))
      response.raise_for_status()
      return response.json()


  def _paginate(url: str, token: str, accept: str = "application/vnd.github+json") -> list[Any]:
      """GET all pages of a paginated endpoint, applying rate-limit retry per request."""
      results: list[Any] = []
      next_url: str | None = url
      while next_url:
          response = _get_with_retry(next_url, _headers(token, accept))
          response.raise_for_status()
          results.extend(response.json())
          next_url = _next_link(response.headers.get("link", ""))
      return results


  def _next_link(link_header: str) -> str | None:
      for part in link_header.split(","):
          url_part, *params = part.strip().split(";")
          if any('rel="next"' in p for p in params):
              return url_part.strip().strip("<>")
      return None


  def _now_utc() -> str:
      return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


  def fetch_traffic_views(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Fetch daily traffic views. Returns list of {date, count, uniques}."""
      data = _get(f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/views", token)
      return [
          {"date": v["timestamp"][:10], "count": v["count"], "uniques": v["uniques"]}
          for v in data.get("views", [])
      ]


  def fetch_traffic_clones(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Fetch daily traffic clones. Returns list of {date, count, uniques}."""
      data = _get(f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/clones", token)
      return [
          {"date": c["timestamp"][:10], "count": c["count"], "uniques": c["uniques"]}
          for c in data.get("clones", [])
      ]


  def fetch_traffic_referrers(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Fetch top referrers snapshot. Returns list of {collected_at, referrer, count, uniques}."""
      data = _get(f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/popular/referrers", token)
      now = _now_utc()
      return [{"collected_at": now, "referrer": r["referrer"], "count": r["count"],
               "uniques": r["uniques"]} for r in data]


  def fetch_traffic_paths(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Fetch top paths snapshot. Returns list of {collected_at, path, title, count, uniques}."""
      data = _get(f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/popular/paths", token)
      now = _now_utc()
      return [{"collected_at": now, "path": p["path"], "title": p["title"],
               "count": p["count"], "uniques": p["uniques"]} for p in data]


  def fetch_stars(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Fetch all star events. Returns list of {starred_at, user}."""
      items = _paginate(
          f"{BASE}/repos/{repo['owner']}/{repo['name']}/stargazers",
          token,
          accept="application/vnd.github.v3.star+json",
      )
      return [{"starred_at": item["starred_at"], "user": item["user"]["login"]} for item in items]


  def fetch_forks(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Fetch all fork events. Returns list of {forked_at, owner}."""
      items = _paginate(f"{BASE}/repos/{repo['owner']}/{repo['name']}/forks", token)
      return [{"forked_at": item["created_at"], "owner": item["owner"]["login"]} for item in items]


  def fetch_releases(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Fetch release asset download counts snapshot. Returns list of {collected_at, tag, asset, download_count}."""
      releases = _paginate(f"{BASE}/repos/{repo['owner']}/{repo['name']}/releases", token)
      now = _now_utc()
      records: list[dict[str, Any]] = []
      for release in releases:
          for asset in release.get("assets", []):
              records.append({
                  "collected_at": now,
                  "tag": release["tag_name"],
                  "asset": asset["name"],
                  "download_count": asset["download_count"],
              })
      return records


  def fetch_metadata(repo: RepoId, token: str) -> dict[str, Any]:
      """Fetch repo metadata snapshot. Returns {date, stars, forks, watchers, open_issues}."""
      data = _get(f"{BASE}/repos/{repo['owner']}/{repo['name']}", token)
      today = datetime.now(UTC).strftime("%Y-%m-%d")
      return {
          "date": today,
          "stars": data["stargazers_count"],
          "forks": data["forks_count"],
          "watchers": data["watchers_count"],
          "open_issues": data["open_issues_count"],
      }


  def fetch_metadata_as_list(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Wrap fetch_metadata to return a list for uniform dispatch in the CLI."""
      return [fetch_metadata(repo, token)]
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  cd github-analytics && uv run pytest tests/test_fetcher.py -v
  ```

  Expected: all 8 tests pass.

- [ ] **Step 5: Run lint and typecheck**

  ```bash
  cd github-analytics && uv run ruff check . && uv run mypy github_analytics/
  ```

- [ ] **Step 6: Commit**

  ```bash
  git add github-analytics/github_analytics/fetcher.py github-analytics/tests/test_fetcher.py
  git commit -m "feat(github-analytics): implement fetcher for all 8 GitHub API endpoints"
  ```

---

## Task 7: CLI Entry Point + E2E Test (collect)

**Files:**
- Create: `github-analytics/github_analytics/__main__.py`
- Create: `github-analytics/tests/test_e2e.py`

The CLI orchestrates per-repo collection with error isolation and proper exit codes.

- [ ] **Step 1: Write failing e2e test for collect**

  Create `github-analytics/tests/test_e2e.py`.

  **Important:** The e2e tests call `cmd_collect()` and `reporter.generate()` as Python
  functions (not subprocess) so that pytest-recording/vcrpy can intercept httpx calls.
  The cassette used here (`e2e_collect.yaml`) bundles all API calls made during a single
  collect run for `karlmdavis/ksoap2-android`.

  ```python
  """End-to-end tests: full collect+report pipeline against VCR cassettes.

  Tests call cmd_collect() and reporter.generate() as Python functions (not subprocesses)
  so that pytest-recording/vcrpy can intercept httpx calls within the test process.
  """
  import json
  import os
  from pathlib import Path
  from typing import Generator

  import pytest

  from github_analytics.__main__ import cmd_collect
  from github_analytics import reporter


  @pytest.fixture()
  def data_repo(tmp_path: Path) -> Path:
      return tmp_path / "data-repo"


  @pytest.fixture()
  def fixture_config(tmp_path: Path) -> Path:
      config = tmp_path / "config.yaml"
      config.write_text("repos:\n  - karlmdavis/ksoap2-android\n")
      return config


  @pytest.fixture(autouse=True)
  def fake_token(monkeypatch: pytest.MonkeyPatch) -> None:
      """Inject a fake token; cassettes don't require real auth."""
      monkeypatch.setenv("GITHUB_TOKEN", "fake-token")


  @pytest.mark.vcr("e2e_collect.yaml")
  def test_collect_creates_ndjson_files(
      data_repo: Path, fixture_config: Path
  ) -> None:
      """Running collect populates the data repo with NDJSON files."""

      class Args:
          data_repo_path = str(data_repo)
          config = str(fixture_config)

      # Temporarily adapt cmd_collect to accept our Args; it reads args.data_repo and args.config
      import argparse
      args = argparse.Namespace(data_repo=str(data_repo), config=str(fixture_config))

      exit_code = cmd_collect(args)
      assert exit_code == 0

      views = data_repo / "karlmdavis" / "ksoap2-android" / "views.ndjson"
      assert views.exists(), f"Expected {views} to exist"
      for line in views.read_text().strip().splitlines():
          record = json.loads(line)
          assert "date" in record
          assert "count" in record


  @pytest.mark.vcr("e2e_collect.yaml")
  def test_collect_is_idempotent(data_repo: Path, fixture_config: Path) -> None:
      """Running collect twice on the same day produces no duplicate records."""
      import argparse
      args = argparse.Namespace(data_repo=str(data_repo), config=str(fixture_config))

      cmd_collect(args)
      cmd_collect(args)  # Second run — cassette replays same responses

      views = data_repo / "karlmdavis" / "ksoap2-android" / "views.ndjson"
      if views.exists():
          lines = views.read_text().strip().splitlines()
          dates = [json.loads(line)["date"] for line in lines if line.strip()]
          assert len(dates) == len(set(dates)), f"Duplicate date records: {dates}"
  ```

- [ ] **Step 2: Create test fixture config**

  Create `github-analytics/tests/fixtures/config_single_repo.yaml`:

  ```yaml
  repos:
    - karlmdavis/ksoap2-android
  ```

- [ ] **Step 3: Run tests to verify they fail**

  ```bash
  cd github-analytics && uv run pytest tests/test_e2e.py -v
  ```

  Expected: `ModuleNotFoundError` or `subprocess` failure — collect command doesn't exist yet.

- [ ] **Step 4: Implement __main__.py**

  Create `github-analytics/github_analytics/__main__.py`:

  ```python
  """CLI entry point: collect and report subcommands."""
  from __future__ import annotations

  import argparse
  import logging
  import os
  import sys
  from pathlib import Path

  from github_analytics.config import load_repos
  from github_analytics import fetcher, writer
  from github_analytics.fetcher import (
      fetch_forks,
      fetch_metadata_as_list,
      fetch_releases,
      fetch_stars,
      fetch_traffic_clones,
      fetch_traffic_paths,
      fetch_traffic_referrers,
      fetch_traffic_views,
  )
  from github_analytics.config import RepoId
  from typing import Callable

  logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
  log = logging.getLogger(__name__)

  # Maps metric name → (fetch function, idempotency key fields)
  # All fetch functions return list[dict[str, Any]]
  _METRICS: list[tuple[str, Callable[[RepoId, str], list[dict[str, Any]]], list[str]]] = [
      ("views", fetch_traffic_views, ["date"]),
      ("clones", fetch_traffic_clones, ["date"]),
      ("metadata", fetch_metadata_as_list, ["date"]),
      ("stars", fetch_stars, ["starred_at", "user"]),
      ("forks", fetch_forks, ["forked_at", "owner"]),
      ("referrers", fetch_traffic_referrers, ["collected_at", "referrer"]),
      ("paths", fetch_traffic_paths, ["collected_at", "path"]),
      ("releases", fetch_releases, ["collected_at", "tag", "asset"]),
  ]


  def _default_config() -> Path:
      return Path(__file__).parent.parent / "config.yaml"


  def cmd_collect(args: argparse.Namespace) -> int:
      token = os.environ.get("GITHUB_TOKEN", "")
      if not token:
          log.error("GITHUB_TOKEN environment variable not set")
          return 1

      data_repo = Path(args.data_repo)
      config_path = Path(args.config) if args.config else _default_config()

      repos = load_repos(config_path, token)
      log.info("Collecting data for %d repos", len(repos))

      errors: list[str] = []

      for repo in repos:
          repo_str = f"{repo['owner']}/{repo['name']}"
          log.info("  → %s", repo_str)
          repo_dir = data_repo / repo["owner"] / repo["name"]

          for metric, fetch_fn, key_fields in _METRICS:
              try:
                  records = fetch_fn(repo, token)
                  dest = repo_dir / f"{metric}.ndjson"
                  for record in records:
                      writer.append_record(dest, record, key_fields)
              except Exception as exc:
                  msg = f"{repo_str}/{metric}: {exc}"
                  log.error("    FAILED: %s", msg)
                  errors.append(msg)

      if errors:
          log.error("%d error(s) occurred during collection:", len(errors))
          for e in errors:
              log.error("  - %s", e)
          return 1

      log.info("Collection complete.")
      return 0


  def main() -> None:
      parser = argparse.ArgumentParser(description="GitHub Analytics Collector")
      sub = parser.add_subparsers(dest="command", required=True)

      collect_parser = sub.add_parser("collect", help="Collect analytics data")
      collect_parser.add_argument("--data-repo", required=True, help="Path to data repository")
      collect_parser.add_argument("--config", default=None, help="Path to config.yaml")

      report_parser = sub.add_parser("report", help="Generate README reports")
      report_parser.add_argument("--data-repo", required=True, help="Path to data repository")

      args = parser.parse_args()

      if args.command == "collect":
          sys.exit(cmd_collect(args))
      elif args.command == "report":
          from github_analytics import reporter
          sys.exit(reporter.generate(Path(args.data_repo)))


  if __name__ == "__main__":
      main()
  ```

  Note: `fetch_metadata` returns a single dict, not a list.
  Add a thin wrapper in `fetcher.py`:

  ```python
  def fetch_metadata_as_list(repo: RepoId, token: str) -> list[dict[str, Any]]:
      """Wrap fetch_metadata to return a list for uniform handling in CLI."""
      return [fetch_metadata(repo, token)]
  ```

- [ ] **Step 5: Record the e2e cassette**

  Add a recording entry to `tests/recording_tests.py` for the e2e cassette.
  Append to that file:

  ```python
  @pytest.mark.vcr("e2e_collect.yaml")
  def test_record_e2e_collect() -> None:
      """Record all API calls made by a full collect run for one repo."""
      import argparse
      from pathlib import Path
      from github_analytics.__main__ import cmd_collect

      args = argparse.Namespace(
          data_repo="/tmp/e2e-cassette-recording",
          config=str(Path(__file__).parent / "fixtures" / "config_single_repo.yaml"),
      )
      cmd_collect(args)
  ```

  Record it:

  ```bash
  cd github-analytics
  GITHUB_TOKEN=<your-pat> uv run pytest tests/recording_tests.py::test_record_e2e_collect \
    --record-mode=new_episodes -v
  ```

  This creates `tests/cassettes/e2e_collect.yaml` covering all 8 endpoint calls
  for `karlmdavis/ksoap2-android`.

- [ ] **Step 6: Run e2e tests**

  ```bash
  cd github-analytics && uv run pytest tests/test_e2e.py -v
  ```

  Expected: both e2e tests pass.

- [ ] **Step 7: Run full CI**

  ```bash
  cd github-analytics && MISE_EXPERIMENTAL=1 mise run :ci
  ```

  Expected: all tests pass, lint clean, mypy strict satisfied.

- [ ] **Step 8: Commit**

  ```bash
  git add github-analytics/github_analytics/__main__.py \
          github-analytics/github_analytics/fetcher.py \
          github-analytics/tests/test_e2e.py \
          github-analytics/tests/fixtures/
  git commit -m "feat(github-analytics): implement CLI collect command with per-repo error isolation"
  ```

---

## Task 8: Reporter Module

**Files:**
- Create: `github-analytics/github_analytics/reporter.py`

The reporter reads NDJSON files and generates README.md files at three levels.
E2e test for the report command is added to `tests/test_e2e.py`.

- [ ] **Step 1: Add report e2e test**

  Append to `github-analytics/tests/test_e2e.py`:

  ```python
  @pytest.mark.vcr("e2e_collect.yaml")
  def test_report_generates_readmes(data_repo: Path, fixture_config: Path) -> None:
      """Running report after collect creates README files at all three levels."""
      import argparse
      args = argparse.Namespace(data_repo=str(data_repo), config=str(fixture_config))

      # First collect data (within the test process — VCR intercepts httpx)
      assert cmd_collect(args) == 0

      # Then generate reports (reads local files only — no HTTP calls, no cassette needed)
      assert reporter.generate(data_repo) == 0

      # Root README must exist with per-metric sections
      root = data_repo / "README.md"
      assert root.exists()
      root_content = root.read_text()
      assert "## Traffic Views" in root_content
      assert "Last updated" in root_content

      # Per-owner README must exist
      assert (data_repo / "karlmdavis" / "README.md").exists()

      # Per-repo README must exist
      assert (data_repo / "karlmdavis" / "ksoap2-android" / "README.md").exists()
  ```

- [ ] **Step 2: Run test to verify it fails**

  ```bash
  cd github-analytics && uv run pytest tests/test_e2e.py::test_report_generates_readmes -v
  ```

  Expected: fails because `reporter` module doesn't exist.

- [ ] **Step 3: Implement reporter.py**

  Create `github-analytics/github_analytics/reporter.py`.
  The reporter reads all NDJSON files and writes README.md files atomically.

  Key design:
  - Root README: one `##` section per metric with a comparison table of all repos.
  - Per-owner README: summary table of all repos for that owner.
  - Per-repo README: monthly traffic table + Mermaid line chart of daily views/clones.

  ```python
  """README generator for the analytics data repository."""
  from __future__ import annotations

  import json
  import logging
  import os
  import tempfile
  from collections import defaultdict
  from datetime import UTC, datetime
  from pathlib import Path
  from typing import Any

  log = logging.getLogger(__name__)


  def generate(data_repo: Path) -> int:
      """Generate all README files. Returns 0 on success, 1 on error."""
      try:
          repos = _discover_repos(data_repo)
          all_data = {repo: _load_repo_data(data_repo, repo) for repo in repos}

          _write_root_readme(data_repo, all_data)
          _write_owner_readmes(data_repo, all_data)
          _write_repo_readmes(data_repo, all_data)
          log.info("Reports generated for %d repos.", len(repos))
          return 0
      except Exception as exc:
          log.error("Reporter failed: %s", exc)
          return 1


  def _discover_repos(data_repo: Path) -> list[tuple[str, str]]:
      """Walk data_repo to find all owner/repo directories containing .ndjson files."""
      repos: list[tuple[str, str]] = []
      if not data_repo.exists():
          return repos
      for owner_dir in sorted(data_repo.iterdir()):
          if not owner_dir.is_dir() or owner_dir.name == "README.md":
              continue
          for repo_dir in sorted(owner_dir.iterdir()):
              if repo_dir.is_dir() and any(repo_dir.glob("*.ndjson")):
                  repos.append((owner_dir.name, repo_dir.name))
      return repos


  def _load_ndjson(path: Path) -> list[dict[str, Any]]:
      if not path.exists():
          return []
      records: list[dict[str, Any]] = []
      for line in path.read_text().splitlines():
          line = line.strip()
          if line:
              records.append(json.loads(line))
      return records


  def _load_repo_data(data_repo: Path, repo: tuple[str, str]) -> dict[str, list[dict[str, Any]]]:
      owner, name = repo
      base = data_repo / owner / name
      return {
          metric: _load_ndjson(base / f"{metric}.ndjson")
          for metric in ["views", "clones", "referrers", "paths", "stars", "forks",
                         "releases", "metadata"]
      }


  def _atomic_write(path: Path, content: str) -> None:
      """Write content to path atomically using temp-file-then-rename."""
      path.parent.mkdir(parents=True, exist_ok=True)
      fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
      try:
          with os.fdopen(fd, "w") as f:
              f.write(content)
          os.replace(tmp, path)
      except Exception:
          try:
              os.unlink(tmp)
          except OSError:
              pass
          raise


  def _now_str() -> str:
      return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


  def _write_root_readme(
      data_repo: Path,
      all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
  ) -> None:
      lines = ["# GitHub Analytics\n", f"_Last updated: {_now_str()}_\n"]

      # Traffic Views section
      lines.append("\n## Traffic Views (last 14 days)\n")
      lines.append("| Repository | Views | Unique Visitors |\n")
      lines.append("|---|---|---|\n")
      for (owner, name), data in sorted(all_data.items()):
          views = data["views"][-14:] if data["views"] else []
          total = sum(r["count"] for r in views)
          uniq = sum(r["uniques"] for r in views)
          lines.append(f"| {owner}/{name} | {total:,} | {uniq:,} |\n")

      # Stars section
      lines.append("\n## Stars (total)\n")
      lines.append("| Repository | Stars |\n")
      lines.append("|---|---|\n")
      for (owner, name), data in sorted(all_data.items()):
          meta = data["metadata"]
          stars = meta[-1]["stars"] if meta else "—"
          lines.append(f"| {owner}/{name} | {stars} |\n")

      # Forks section
      lines.append("\n## Forks (total)\n")
      lines.append("| Repository | Forks |\n")
      lines.append("|---|---|\n")
      for (owner, name), data in sorted(all_data.items()):
          meta = data["metadata"]
          forks = meta[-1]["forks"] if meta else "—"
          lines.append(f"| {owner}/{name} | {forks} |\n")

      _atomic_write(data_repo / "README.md", "".join(lines))


  def _write_owner_readmes(
      data_repo: Path,
      all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
  ) -> None:
      by_owner: dict[str, list[tuple[str, dict[str, list[dict[str, Any]]]]]] = defaultdict(list)
      for (owner, name), data in all_data.items():
          by_owner[owner].append((name, data))

      for owner, repos in by_owner.items():
          lines = [f"# {owner}\n", f"_Last updated: {_now_str()}_\n\n"]
          lines.append("| Repository | Stars | Forks | 7d Views | 7d Clones |\n")
          lines.append("|---|---|---|---|---|\n")
          for name, data in sorted(repos):
              meta = data["metadata"][-1] if data["metadata"] else {}
              views_7d = sum(r["count"] for r in data["views"][-7:])
              clones_7d = sum(r["count"] for r in data["clones"][-7:])
              lines.append(
                  f"| [{name}]({name}/README.md) | {meta.get('stars', '—')} |"
                  f" {meta.get('forks', '—')} | {views_7d:,} | {clones_7d:,} |\n"
              )
          _atomic_write(data_repo / owner / "README.md", "".join(lines))


  def _write_repo_readmes(
      data_repo: Path,
      all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
  ) -> None:
      for (owner, name), data in all_data.items():
          lines = [f"# {owner}/{name}\n", f"_Last updated: {_now_str()}_\n"]
          lines.extend(_traffic_table(data))
          lines.extend(_mermaid_chart(data))
          if data["releases"]:
              lines.extend(_releases_table(data))
          _atomic_write(data_repo / owner / name / "README.md", "".join(lines))


  def _traffic_table(data: dict[str, list[dict[str, Any]]]) -> list[str]:
      views_by_month: dict[str, dict[str, int]] = defaultdict(lambda: {"views": 0, "uniques": 0, "clones": 0})
      for r in data["views"]:
          month = r["date"][:7]
          views_by_month[month]["views"] += r["count"]
          views_by_month[month]["uniques"] += r["uniques"]
      for r in data["clones"]:
          month = r["date"][:7]
          views_by_month[month]["clones"] += r["count"]
      if not views_by_month:
          return []
      lines = ["\n## Traffic\n", "| Month | Views | Unique Visitors | Clones |\n",
               "|---|---|---|---|\n"]
      for month in sorted(views_by_month):
          m = views_by_month[month]
          lines.append(f"| {month} | {m['views']:,} | {m['uniques']:,} | {m['clones']:,} |\n")
      return lines


  def _mermaid_chart(data: dict[str, list[dict[str, Any]]]) -> list[str]:
      if not data["views"]:
          return []
      lines = ["\n```mermaid\nxychart-beta\n  title \"Daily Views\"\n  x-axis ["]
      dates = [r["date"] for r in data["views"][-30:]]
      counts = [str(r["count"]) for r in data["views"][-30:]]
      lines.append(", ".join(f'"{d}"' for d in dates))
      lines.append("]\n  bar [")
      lines.append(", ".join(counts))
      lines.append("]\n```\n")
      return lines


  def _releases_table(data: dict[str, list[dict[str, Any]]]) -> list[str]:
      # Latest download count per tag+asset
      latest: dict[tuple[str, str], int] = {}
      for r in data["releases"]:
          key = (r["tag"], r["asset"])
          latest[key] = r["download_count"]
      if not latest:
          return []
      lines = ["\n## Release Downloads\n", "| Tag | Asset | Downloads |\n", "|---|---|---|\n"]
      for (tag, asset), count in sorted(latest.items()):
          lines.append(f"| {tag} | {asset} | {count:,} |\n")
      return lines
  ```

- [ ] **Step 4: Run tests**

  ```bash
  cd github-analytics && uv run pytest tests/test_e2e.py -v
  ```

  Expected: all 3 e2e tests pass.

- [ ] **Step 5: Run full CI**

  ```bash
  cd github-analytics && MISE_EXPERIMENTAL=1 mise run :ci
  ```

  Expected: all tests pass, lint clean, mypy strict satisfied.

- [ ] **Step 6: Commit**

  ```bash
  git add github-analytics/github_analytics/reporter.py \
          github-analytics/tests/test_e2e.py
  git commit -m "feat(github-analytics): implement reporter with 3-level README generation"
  ```

---

## Task 9: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/github-analytics.yml`

- [ ] **Step 1: Create workflow file**

  Create `.github/workflows/github-analytics.yml`:

  ```yaml
  name: Collect GitHub Analytics

  on:
    schedule:
      - cron: '0 6 * * *'   # Daily at 6 AM UTC
    workflow_dispatch:        # Allow manual trigger

  concurrency:
    group: analytics-collection
    cancel-in-progress: false  # Serialize runs; don't cancel in-progress

  jobs:
    collect:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4

        - name: Checkout data repo
          uses: actions/checkout@v4
          with:
            repository: justdavis-family/github-analytics-data
            token: ${{ secrets.ANALYTICS_DATA_PAT }}
            path: analytics-data

        - uses: jdx/mise-action@v2

        - name: Collect analytics
          id: collect
          continue-on-error: true
          env:
            GITHUB_TOKEN: ${{ secrets.ANALYTICS_DATA_PAT }}
          run: >
            MISE_EXPERIMENTAL=1 mise run '//github-analytics:collect'
            -- --data-repo ${{ github.workspace }}/analytics-data

        - name: Generate reports
          id: report
          continue-on-error: true
          run: >
            MISE_EXPERIMENTAL=1 mise run '//github-analytics:report'
            -- --data-repo ${{ github.workspace }}/analytics-data

        - name: Commit and push data
          run: |
            cd analytics-data
            git config user.name "GitHub Analytics Bot"
            git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
            git add -A
            git diff --cached --quiet \
              || git commit -m "data: collect analytics $(date -u +%Y-%m-%d)"
            git push

        - name: Fail if collection had errors
          if: steps.collect.outcome == 'failure' || steps.report.outcome == 'failure'
          run: exit 1
  ```

- [ ] **Step 2: Commit workflow**

  ```bash
  git add .github/workflows/github-analytics.yml
  git commit -m "feat(github-analytics): add scheduled GitHub Actions collection workflow"
  ```

---

## Task 10: Data Repo Setup + Live Verification

**Prerequisites:** GitHub PAT with `repo` scope from the `karlmdavis` account.

- [ ] **Step 1: Create the data repository**

  ```bash
  gh repo create justdavis-family/github-analytics-data \
    --public \
    --description "GitHub analytics data collected by justdavis-family/justdavis"
  ```

  Initialize with a placeholder README:

  ```bash
  cd /tmp && git clone https://github.com/justdavis-family/github-analytics-data
  cd github-analytics-data
  echo "# GitHub Analytics Data\n\nPopulated by the analytics collector workflow." > README.md
  git add README.md
  git commit -m "init: initial commit"
  git push
  ```

- [ ] **Step 2: Create and store the PAT**

  In a browser: go to `github.com/settings/tokens` → "Generate new token (classic)" →
    name "ANALYTICS_DATA_PAT" → select `repo` scope → generate.

  Store the token as a secret:

  ```bash
  gh secret set ANALYTICS_DATA_PAT \
    --repo justdavis-family/justdavis \
    --body "<paste-token-here>"
  ```

- [ ] **Step 3: Push the feature branch and open a PR**

  ```bash
  git push -u origin feature/github-analytics
  gh pr create \
    --title "feat: GitHub analytics collector" \
    --body "$(cat <<'EOF'
  ## Summary
  - Adds a daily GitHub Actions workflow that collects all available analytics
    for all configured repos and stores them as NDJSON in a dedicated data repository.
  - Adds a reporter that generates human-readable README files at root, per-owner,
    and per-repo levels.
  - Uses GitHub Actions → Mise → uv invocation chain for local/CI parity.

  ## Test plan
  - `MISE_EXPERIMENTAL=1 mise run //github-analytics:ci` passes locally.
  - VCR cassettes cover all 8 API endpoint types.
  - E2e tests verify collect + report pipeline and idempotency.

  ## Success Criteria
  - [ ] PR description complete.
  - [ ] No stubbed/incomplete code.
  - [ ] All CI checks pass.
  - [ ] Work committed and pushed.
  - [ ] `MISE_EXPERIMENTAL=1 mise run //github-analytics:ci` passes.
  - [ ] Manual workflow run succeeds and populates analytics-data repo.
  - [ ] Idempotency verified: two runs on same day produce no duplicate records.

  Closes #<issue-number-if-any>
  EOF
  )"
  ```

- [ ] **Step 4: Merge PR and run workflow manually**

  After CI passes and PR is merged:

  ```bash
  # Trigger a manual workflow run
  gh workflow run github-analytics.yml
  # Watch the run
  gh run watch
  ```

  Expected: workflow completes successfully.
  Verify: `gh browse https://github.com/justdavis-family/github-analytics-data`
  shows NDJSON files and a rendered README.

- [ ] **Step 5: Verify idempotency**

  Trigger the workflow a second time:

  ```bash
  gh workflow run github-analytics.yml && gh run watch
  ```

  Then clone the data repo and check for duplicate records:

  ```bash
  cd /tmp && git clone https://github.com/justdavis-family/github-analytics-data
  # Check a views.ndjson for duplicate dates
  for f in github-analytics-data/*/*/views.ndjson; do
    python3 -c "
  import json
  lines = open('$f').read().splitlines()
  dates = [json.loads(l)['date'] for l in lines if l]
  assert len(dates) == len(set(dates)), f'DUPLICATE DATES in $f: {dates}'
  print(f'OK: $f ({len(dates)} records, no duplicates)')
  "
  done
  ```

- [ ] **Step 6: Verify 48-hour scheduling**

  After waiting ~24 hours, check that the scheduled run completed:

  ```bash
  gh run list --workflow=github-analytics.yml --limit=5
  ```

  Expected: at least 2 successful runs visible.

---

## Verification Checklist

- [ ] `MISE_EXPERIMENTAL=1 mise run //github-analytics:ci` passes (tests green, lint clean,
      mypy strict satisfied).
- [ ] Manual workflow run succeeds: data repo receives new NDJSON files and README updates.
- [ ] `github.com/justdavis-family/github-analytics-data` renders a README
      with per-metric comparison tables.
- [ ] Idempotency confirmed: two runs on same day produce no duplicate records.
- [ ] Smoke test: `MISE_EXPERIMENTAL=1 mise run //github-analytics:collect:smoke` exits 0
      and produces files under `/tmp/analytics-smoke-*/`.
- [ ] Scheduled workflow runs confirmed after 48 hours.
