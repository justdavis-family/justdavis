"""CLI entry point: collect and report subcommands."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from collections import defaultdict
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import structlog

from github_analytics import writer
from github_analytics.config import RepoId, load_repos
from github_analytics.fetcher import (
    fetch_forks,
    fetch_metadata_as_list,
    fetch_releases,
    fetch_stars,
    fetch_traffic_clones,
    fetch_traffic_paths,
    fetch_traffic_referrers,
    fetch_traffic_views,
    fetch_workflow_runs,
)

# Fetch function type: (client, sem, repo, token) → (records, io_s, wait_s)
_FetchFn = Callable[
    [httpx.AsyncClient, asyncio.Semaphore, RepoId, str],
    Coroutine[Any, Any, tuple[list[dict[str, Any]], float, float]],
]

# Maps metric name → (fetch function, idempotency key fields, upsert).
# upsert=True: re-running overwrites records with the same key so that partial
#   data collected early in the day is replaced by a more complete value later.
# upsert=False: append-only; correct for immutable per-event data (stars, forks).
_WF_KEYS = ["date", "name", "path", "workflow_id", "status", "conclusion"]
_METRICS: list[tuple[str, _FetchFn, list[str], bool]] = [
    ("views", fetch_traffic_views, ["date"], True),
    ("clones", fetch_traffic_clones, ["date"], True),
    ("metadata", fetch_metadata_as_list, ["date"], True),
    ("stars", fetch_stars, ["starred_at", "user"], False),
    ("forks", fetch_forks, ["forked_at", "owner"], False),
    ("referrers", fetch_traffic_referrers, ["date", "referrer"], True),
    ("paths", fetch_traffic_paths, ["date", "path"], True),
    ("releases", fetch_releases, ["date", "tag", "asset"], True),
    ("workflow_runs", fetch_workflow_runs, _WF_KEYS, True),
]


@dataclass
class _Timing:
    io: float = 0.0
    wait: float = 0.0
    compute: float = 0.0


@dataclass
class _MetricResult:
    metric: str
    count: int = 0
    error: str | None = None


@dataclass
class _RepoResult:
    repo_str: str
    elapsed: float = 0.0
    metric_results: list[_MetricResult] = field(default_factory=list)

    @property
    def errors(self) -> list[str]:
        return [f"{self.repo_str}/{r.metric}: {r.error}" for r in self.metric_results if r.error]

    @property
    def counts(self) -> dict[str, int]:
        return {r.metric: r.count for r in self.metric_results if not r.error and r.count > 0}


def _default_config() -> Path:
    """Return the default config.yaml path relative to the package."""
    return Path(__file__).parent.parent / "config.yaml"


async def _collect_metric(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    metric: str,
    fetch_fn: _FetchFn,
    key_fields: list[str],
    upsert: bool,
    repo_dir: Path,
    timings: dict[str, _Timing],
    token: str,
) -> _MetricResult:
    """Fetch one metric for one repo and write results. Returns a MetricResult."""
    log = structlog.get_logger().bind(repo=f"{repo['owner']}/{repo['name']}", metric=metric)
    try:
        log.debug("fetch.start")
        t0 = time.perf_counter()
        records, io_s, wait_s = await fetch_fn(client, sem, repo, token)
        compute_s = time.perf_counter() - t0 - io_s - wait_s

        # Accumulate timing (safe: asyncio is single-threaded)
        timings[metric].io += io_s
        timings[metric].wait += wait_s
        timings[metric].compute += max(0.0, compute_s)

        t_write = time.perf_counter()
        dest = repo_dir / f"{metric}.ndjson"
        written = writer.append_records(dest, records, key_fields, upsert=upsert)
        timings[metric].compute += max(0.0, time.perf_counter() - t_write)

        log.debug("fetch.done", fetched=len(records), written=written, io_ms=round(io_s * 1000))
        return _MetricResult(metric=metric, count=written)
    except Exception as exc:
        log.warning("fetch.error", error=str(exc))
        return _MetricResult(metric=metric, error=str(exc))


async def _collect_repo(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    data_repo: Path,
    timings: dict[str, _Timing],
    token: str,
) -> _RepoResult:
    """Fetch all metrics for one repo concurrently."""
    repo_str = f"{repo['owner']}/{repo['name']}"
    repo_dir = data_repo / repo["owner"] / repo["name"]
    t0 = time.perf_counter()

    metric_tasks = [
        _collect_metric(client, sem, repo, metric, fetch_fn, key_fields, upsert, repo_dir, timings, token)
        for metric, fetch_fn, key_fields, upsert in _METRICS
    ]
    results = await asyncio.gather(*metric_tasks)

    elapsed = time.perf_counter() - t0
    repo_result = _RepoResult(repo_str=repo_str, elapsed=elapsed, metric_results=list(results))

    # Print progress line immediately when repo completes
    if repo_result.errors:
        print(f"  \u2717 {repo_str:<45} {elapsed:5.1f}s  ERROR")
    else:
        counts_str = " ".join(f"{m}:{c}" for m, c in repo_result.counts.items())
        print(f"  \u2714 {repo_str:<45} {elapsed:5.1f}s  ({counts_str})")

    return repo_result


def _print_timing_table(timings: dict[str, _Timing]) -> None:
    """Print the timing breakdown table to stdout."""
    if not timings:
        return
    print("\nTime breakdown (seconds):")
    print(f"  {'endpoint':<20} {'I/O':>6}  {'wait':>6}  {'compute':>7}")
    print(f"  {'-' * 20} {'-' * 6}  {'-' * 6}  {'-' * 7}")
    total = _Timing()
    for metric in sorted(timings):
        t = timings[metric]
        wait_str = f"{t.wait:6.1f}" if t.wait > 0.001 else "     -"
        print(f"  {metric:<20} {t.io:6.1f}  {wait_str}  {t.compute:7.2f}")
        total.io += t.io
        total.wait += t.wait
        total.compute += t.compute
    print(f"  {'TOTAL':<20} {total.io:6.1f}  {total.wait:6.1f}  {total.compute:7.2f}")


async def _collect_async(args: argparse.Namespace, token: str, repos: list[RepoId]) -> int:
    """Async implementation of the collect subcommand."""
    max_concurrent: int = args.max_concurrent
    data_repo = Path(args.data_repo)

    print(f"Collecting {len(repos)} repo(s) ({max_concurrent} concurrent max)...")

    timings: dict[str, _Timing] = defaultdict(_Timing)
    t_total = time.perf_counter()

    limits = httpx.Limits(
        max_keepalive_connections=max_concurrent,
        max_connections=max_concurrent,
    )
    sem = asyncio.Semaphore(max_concurrent)

    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(30.0)) as client:
        repo_tasks = [_collect_repo(client, sem, repo, data_repo, timings, token) for repo in repos]
        repo_results = await asyncio.gather(*repo_tasks)

    elapsed_total = time.perf_counter() - t_total
    print(f"Done in {elapsed_total:.1f}s.")
    _print_timing_table(timings)

    all_errors = [err for result in repo_results for err in result.errors]
    if all_errors:
        print(f"\n{len(all_errors)} error(s) occurred during collection:")
        for err in all_errors:
            print(f"  - {err}")
        return 1
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    """Run the collect subcommand. Returns 0 on full success, 1 if any error."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("ERROR: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        return 1
    _configure_logging(args.verbose, token)
    # Resolve repos synchronously before entering the event loop — load_repos
    # uses blocking httpx.get() for org:/user: wildcard expansion.
    config_path = Path(args.config) if args.config else _default_config()
    repos = load_repos(config_path, token)
    return asyncio.run(_collect_async(args, token, repos))


def _configure_logging(verbose: bool, token: str = "") -> None:
    """Configure structlog for the CLI.

    When a token is supplied, a processor is added that redacts any occurrence
    of the token value from log event strings, providing defence-in-depth
    against accidental credential leakage into log output.
    """
    level = logging.DEBUG if verbose else logging.WARNING
    processors: list[Any] = [structlog.stdlib.add_log_level]
    if token:
        _tok = token  # capture in closure

        def _scrub_token(_logger: object, _method: str, event_dict: dict[str, Any]) -> dict[str, Any]:
            return {k: v.replace(_tok, "***") if isinstance(v, str) else v for k, v in event_dict.items()}

        processors.append(_scrub_token)
    processors.append(structlog.dev.ConsoleRenderer())
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
    )


def main() -> None:
    """Parse CLI arguments and dispatch to the appropriate subcommand."""
    parser = argparse.ArgumentParser(description="GitHub Analytics Collector")
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable debug-level structured logging",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    collect_parser = sub.add_parser("collect", help="Collect analytics data")
    collect_parser.add_argument(
        "--data-repo",
        required=True,
        dest="data_repo",
        help="Path to data repository",
    )
    collect_parser.add_argument("--config", default=None, help="Path to config.yaml")
    collect_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=20,
        dest="max_concurrent",
        help="Maximum concurrent HTTP requests (default: 20)",
    )

    report_parser = sub.add_parser("report", help="Generate README reports")
    report_parser.add_argument(
        "--data-repo",
        required=True,
        dest="data_repo",
        help="Path to data repository",
    )

    args = parser.parse_args()

    if args.command == "collect":
        sys.exit(cmd_collect(args))
    elif args.command == "report":
        from github_analytics import reporter  # noqa: PLC0415

        sys.exit(reporter.generate(Path(args.data_repo)))


if __name__ == "__main__":
    main()
