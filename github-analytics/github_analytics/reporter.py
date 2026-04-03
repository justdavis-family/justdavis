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
        if not owner_dir.is_dir():
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if repo_dir.is_dir() and any(repo_dir.glob("*.ndjson")):
                repos.append((owner_dir.name, repo_dir.name))
    return repos


def _load_ndjson(path: Path) -> list[dict[str, Any]]:
    """Read an NDJSON file and return all records as a list."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped:
            records.append(json.loads(stripped))
    return records


def _load_repo_data(data_repo: Path, repo: tuple[str, str]) -> dict[str, list[dict[str, Any]]]:
    """Load all NDJSON files for a single repo."""
    owner, name = repo
    base = data_repo / owner / name
    return {
        metric: _load_ndjson(base / f"{metric}.ndjson")
        for metric in ["views", "clones", "referrers", "paths", "stars", "forks", "releases", "metadata"]
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
    """Return the current UTC time as a human-readable string."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _write_root_readme(
    data_repo: Path,
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> None:
    """Write the root README with per-metric comparison tables."""
    lines = ["# GitHub Analytics\n", f"_Last updated: {_now_str()}_\n"]

    lines.append("\n## Traffic Views (last 14 days)\n")
    lines.append("| Repository | Views | Unique Visitors |\n")
    lines.append("|---|---|---|\n")
    for (owner, name), data in sorted(all_data.items()):
        views = data["views"][-14:] if data["views"] else []
        total = sum(r["count"] for r in views)
        uniq = sum(r["uniques"] for r in views)
        lines.append(f"| {owner}/{name} | {total:,} | {uniq:,} |\n")

    lines.append("\n## Traffic Clones (last 14 days)\n")
    lines.append("| Repository | Clones | Unique Cloners |\n")
    lines.append("|---|---|---|\n")
    for (owner, name), data in sorted(all_data.items()):
        clones = data["clones"][-14:] if data["clones"] else []
        total = sum(r["count"] for r in clones)
        uniq = sum(r["uniques"] for r in clones)
        lines.append(f"| {owner}/{name} | {total:,} | {uniq:,} |\n")

    lines.append("\n## Stars (total)\n")
    lines.append("| Repository | Stars |\n")
    lines.append("|---|---|\n")
    for (owner, name), data in sorted(all_data.items()):
        meta = data["metadata"]
        stars = meta[-1]["stars"] if meta else "—"
        lines.append(f"| {owner}/{name} | {stars} |\n")

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
    """Write per-owner README files with summary tables."""
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
    """Write per-repo README files with traffic tables and Mermaid charts."""
    for (owner, name), data in all_data.items():
        lines: list[str] = [f"# {owner}/{name}\n", f"_Last updated: {_now_str()}_\n"]
        lines.extend(_traffic_table(data))
        lines.extend(_mermaid_chart(data))
        if data["releases"]:
            lines.extend(_releases_table(data))
        _atomic_write(data_repo / owner / name / "README.md", "".join(lines))


def _traffic_table(data: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Build a monthly traffic table from views and clones data."""
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
    lines = ["\n## Traffic\n", "| Month | Views | Unique Visitors | Clones |\n", "|---|---|---|---|\n"]
    for month in sorted(views_by_month):
        m = views_by_month[month]
        lines.append(f"| {month} | {m['views']:,} | {m['uniques']:,} | {m['clones']:,} |\n")
    return lines


def _mermaid_chart(data: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Build a Mermaid xychart-beta bar chart for daily views."""
    if not data["views"]:
        return []
    recent = data["views"][-30:]
    dates = [r["date"] for r in recent]
    counts = [str(r["count"]) for r in recent]
    lines = ['\n```mermaid\nxychart-beta\n  title "Daily Views"\n  x-axis [']
    lines.append(", ".join(f'"{d}"' for d in dates))
    lines.append("]\n  bar [")
    lines.append(", ".join(counts))
    lines.append("]\n```\n")
    return lines


def _releases_table(data: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Build a release download counts table from the latest snapshot per tag+asset."""
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
