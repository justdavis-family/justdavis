"""CLI entry point: collect and report subcommands."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

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
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Maps metric name → (fetch function, idempotency key fields).
# All fetch functions return list[dict[str, Any]].
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
    """Return the default config.yaml path relative to the package."""
    return Path(__file__).parent.parent / "config.yaml"


def cmd_collect(args: argparse.Namespace) -> int:
    """Run the collect subcommand. Returns 0 on full success, 1 if any error."""
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
        log.info("  \u2192 %s", repo_str)
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
    """Parse CLI arguments and dispatch to the appropriate subcommand."""
    parser = argparse.ArgumentParser(description="GitHub Analytics Collector")
    sub = parser.add_subparsers(dest="command", required=True)

    collect_parser = sub.add_parser("collect", help="Collect analytics data")
    collect_parser.add_argument(
        "--data-repo",
        required=True,
        dest="data_repo",
        help="Path to data repository",
    )
    collect_parser.add_argument("--config", default=None, help="Path to config.yaml")

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
        from github_analytics import reporter  # type: ignore[attr-defined]  # noqa: PLC0415

        sys.exit(reporter.generate(Path(args.data_repo)))


if __name__ == "__main__":
    main()
