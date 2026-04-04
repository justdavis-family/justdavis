"""README generator for the analytics data repository."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Metrics loaded from NDJSON files for each repo.
_METRICS = [
    "views",
    "clones",
    "referrers",
    "paths",
    "stars",
    "forks",
    "releases",
    "metadata",
    "commit_activity",
]

_COMMITS_TABLE_WEEKS = 26


def generate(data_repo: Path) -> int:
    """Generate all README files and SVG charts. Returns 0 on success, 1 on error."""
    try:
        repos = _discover_repos(data_repo)
        all_data = {repo: _load_repo_data(data_repo, repo) for repo in repos}

        _write_multi_repo_readme(
            data_repo / "README.md",
            [
                data_repo / "unique_visitors.svg",
                data_repo / "unique_clones.svg",
                data_repo / "commits_per_week.svg",
            ],
            "# GitHub Analytics",
            all_data,
        )
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
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
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
    return {metric: _load_ndjson(base / f"{metric}.ndjson") for metric in _METRICS}


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


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def _date_to_quarter(date_str: str) -> str:
    """Convert 'YYYY-MM-DD' to 'YYYY-Q1' etc."""
    month = int(date_str[5:7])
    q = (month - 1) // 3 + 1
    return f"{date_str[:4]}-Q{q}"


def _date_to_month(date_str: str) -> str:
    """Convert 'YYYY-MM-DD' to 'YYYY-MM'."""
    return date_str[:7]


def _avg_by_period(
    records: list[dict[str, Any]],
    date_field: str,
    value_field: str,
    period_fn: Callable[[str], str],
) -> dict[str, float]:
    """Average daily values grouped by period (quarter or month)."""
    by_period: dict[str, list[float]] = defaultdict(list)
    for r in records:
        period = period_fn(r[date_field])
        by_period[period].append(float(r[value_field]))
    return {p: sum(vals) / len(vals) for p, vals in sorted(by_period.items())}


def _last_n_week_starts(all_commit_activity: list[dict[str, Any]], n: int) -> set[str]:
    """Return the last n week_start values sorted across all commit_activity records."""
    weeks = sorted({r["week_start"] for r in all_commit_activity})
    return set(weeks[-n:])


# ---------------------------------------------------------------------------
# Vega-Lite SVG rendering
# ---------------------------------------------------------------------------


def _vegalite_to_svg(spec: dict[str, Any]) -> str:
    """Render a Vega-Lite spec dict to SVG string via vl-convert-python."""
    import vl_convert as vlc  # noqa: PLC0415

    return vlc.vegalite_to_svg(json.dumps(spec))


def _stacked_area_spec(
    values: list[dict[str, Any]],
    x_field: str,
    y_field: str,
    color_field: str,
    title: str,
    y_title: str,
) -> dict[str, Any]:
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "width": 800,
        "height": 300,
        "title": title,
        "data": {"values": values},
        "mark": "area",
        "encoding": {
            "x": {"field": x_field, "type": "temporal", "title": "Date"},
            "y": {"field": y_field, "type": "quantitative", "stack": True, "title": y_title},
            "color": {"field": color_field, "type": "nominal", "title": "Repository"},
        },
    }


def _build_views_svg(
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
    value_key: str,
    title: str,
    y_title: str,
) -> str | None:
    """Build a stacked area SVG for unique visitors or views across all repos."""
    points: list[dict[str, Any]] = []
    for (owner, name), data in all_data.items():
        for r in data["views"]:
            points.append({"date": r["date"], "repo": f"{owner}/{name}", "value": r[value_key]})
    if not points:
        return None
    return _vegalite_to_svg(_stacked_area_spec(points, "date", "value", "repo", title, y_title))


def _build_clones_svg(
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
    value_key: str,
    title: str,
    y_title: str,
) -> str | None:
    """Build a stacked area SVG for unique clones or clones across all repos."""
    points: list[dict[str, Any]] = []
    for (owner, name), data in all_data.items():
        for r in data["clones"]:
            points.append({"date": r["date"], "repo": f"{owner}/{name}", "value": r[value_key]})
    if not points:
        return None
    return _vegalite_to_svg(_stacked_area_spec(points, "date", "value", "repo", title, y_title))


def _build_commits_svg(
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> str | None:
    """Build a stacked area SVG for commits per week across all repos."""
    points: list[dict[str, Any]] = []
    for (owner, name), data in all_data.items():
        for r in data["commit_activity"]:
            points.append({"week": r["week_start"], "repo": f"{owner}/{name}", "commits": r["total"]})
    if not points:
        return None
    return _vegalite_to_svg(
        _stacked_area_spec(points, "week", "commits", "repo", "Commits per Week", "Commits")
    )


# ---------------------------------------------------------------------------
# Multi-repo content builders
# ---------------------------------------------------------------------------


def _multi_repo_sections(
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
    svg_paths: list[Path],
) -> list[str]:
    """Build the body sections for a multi-repo README.

    svg_paths: [unique_visitors_path, unique_clones_path, commits_path]
    """
    lines: list[str] = []

    # 1 & 2: Stacked area charts (SVGs written by caller; here we just emit references)
    uv_svg, uc_svg, cw_svg = svg_paths
    lines.append("\n## Unique Visitors per Day\n\n")
    lines.append(f"![Unique Visitors per Day]({uv_svg.name})\n")
    lines.append("\n## Unique Clones per Day\n\n")
    lines.append(f"![Unique Clones per Day]({uc_svg.name})\n")

    # 3: Quarterly traffic tables (4 tables)
    lines.extend(_quarterly_traffic_tables(all_data))

    # 4: Current totals table
    lines.extend(_current_totals_table(all_data))

    # 5: Commits per week chart
    lines.append("\n## Commits per Week\n\n")
    lines.append(f"![Commits per Week]({cw_svg.name})\n")

    # 6: Commits quarterly table
    lines.extend(_commits_quarterly_table(all_data))

    return lines


def _quarterly_traffic_tables(
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> list[str]:
    """Build 4 quarterly traffic tables: unique visitors, views, unique clones, clones."""
    metrics = [
        ("views", "uniques", "Unique Visitors (avg/day)"),
        ("views", "count", "Views (avg/day)"),
        ("clones", "uniques", "Unique Clones (avg/day)"),
        ("clones", "count", "Clones (avg/day)"),
    ]
    lines: list[str] = []
    for ndjson_key, value_field, heading in metrics:
        # Collect all quarters present in this dataset
        quarters: set[str] = set()
        repo_avgs: dict[str, dict[str, float]] = {}
        for (owner, name), data in all_data.items():
            avgs = _avg_by_period(data[ndjson_key], "date", value_field, _date_to_quarter)
            quarters |= set(avgs.keys())
            repo_avgs[f"{owner}/{name}"] = avgs

        if not quarters:
            continue

        sorted_quarters = sorted(quarters)
        lines.append(f"\n## {heading}\n\n")
        header = "| Repository | " + " | ".join(sorted_quarters) + " |\n"
        lines.append(header)
        lines.append("|---|" + "---|" * len(sorted_quarters) + "\n")
        for repo_key in sorted(repo_avgs):
            avgs = repo_avgs[repo_key]
            cells = " | ".join(f"{avgs.get(q, 0):.1f}" for q in sorted_quarters)
            lines.append(f"| {repo_key} | {cells} |\n")

    return lines


def _current_totals_table(
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> list[str]:
    """Build a table of current stars and forks per repo."""
    lines = ["\n## Current Totals\n\n", "| Repository | Stars | Forks |\n", "|---|---|---|\n"]
    for (owner, name), data in sorted(all_data.items()):
        meta = data["metadata"]
        stars = meta[-1]["stars"] if meta else "—"
        forks = meta[-1]["forks"] if meta else "—"
        lines.append(f"| {owner}/{name} | {stars} | {forks} |\n")
    return lines


def _commits_quarterly_table(
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> list[str]:
    """Build a quarterly commits table for the last _COMMITS_TABLE_WEEKS weeks."""
    # Gather all week_starts from all repos to determine the last N
    all_activity = [r for data in all_data.values() for r in data["commit_activity"]]
    if not all_activity:
        return []

    last_n = _last_n_week_starts(all_activity, _COMMITS_TABLE_WEEKS)

    quarters: set[str] = set()
    repo_totals: dict[str, dict[str, int]] = {}
    for (owner, name), data in all_data.items():
        by_quarter: dict[str, int] = defaultdict(int)
        for r in data["commit_activity"]:
            if r["week_start"] in last_n:
                q = _date_to_quarter(r["week_start"])
                quarters.add(q)
                by_quarter[q] += r["total"]
        repo_totals[f"{owner}/{name}"] = dict(by_quarter)

    if not quarters:
        return []

    sorted_quarters = sorted(quarters)
    lines = [f"\n## Commits per Week (last {_COMMITS_TABLE_WEEKS} weeks)\n\n"]
    lines.append("| Repository | " + " | ".join(sorted_quarters) + " |\n")
    lines.append("|---|" + "---|" * len(sorted_quarters) + "\n")
    for repo_key in sorted(repo_totals):
        totals = repo_totals[repo_key]
        cells = " | ".join(str(totals.get(q, 0)) for q in sorted_quarters)
        lines.append(f"| {repo_key} | {cells} |\n")
    return lines


# ---------------------------------------------------------------------------
# Multi-repo README writers
# ---------------------------------------------------------------------------


def _write_multi_repo_readme(
    readme_path: Path,
    svg_paths: list[Path],
    heading: str,
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> None:
    """Write a multi-repo README and its companion SVG files."""
    uv_svg_path, uc_svg_path, cw_svg_path = svg_paths

    # Generate and write SVGs (skip section if no data)
    uv_svg = _build_views_svg(all_data, "uniques", "Unique Visitors per Day", "Unique Visitors/day")
    if uv_svg:
        _atomic_write(uv_svg_path, uv_svg)

    uc_svg = _build_clones_svg(all_data, "uniques", "Unique Clones per Day", "Unique Clones/day")
    if uc_svg:
        _atomic_write(uc_svg_path, uc_svg)

    cw_svg = _build_commits_svg(all_data)
    if cw_svg:
        _atomic_write(cw_svg_path, cw_svg)

    lines: list[str] = [f"{heading}\n\n", f"_Last updated: {_now_str()}_\n"]

    if uv_svg or uc_svg:
        lines.extend(_multi_repo_sections(all_data, svg_paths))
    else:
        # Fallback when no traffic data yet — just show current totals
        lines.extend(_current_totals_table(all_data))

    _atomic_write(readme_path, "".join(lines))


def _write_root_readme(
    data_repo: Path,
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> None:
    _write_multi_repo_readme(
        data_repo / "README.md",
        [
            data_repo / "unique_visitors.svg",
            data_repo / "unique_clones.svg",
            data_repo / "commits_per_week.svg",
        ],
        "# GitHub Analytics",
        all_data,
    )


def _write_owner_readmes(
    data_repo: Path,
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> None:
    by_owner: dict[str, dict[tuple[str, str], dict[str, list[dict[str, Any]]]]] = defaultdict(dict)
    for repo, data in all_data.items():
        by_owner[repo[0]][repo] = data

    for owner, owner_data in by_owner.items():
        _write_multi_repo_readme(
            data_repo / owner / "README.md",
            [
                data_repo / owner / "unique_visitors.svg",
                data_repo / owner / "unique_clones.svg",
                data_repo / owner / "commits_per_week.svg",
            ],
            f"# {owner}",
            owner_data,
        )


# ---------------------------------------------------------------------------
# Single-repo content builders
# ---------------------------------------------------------------------------


def _mermaid_line(dates: list[str], values: list[int | float], title: str) -> list[str]:
    """Build a MermaidJS xychart-beta line chart."""
    if not dates:
        return []
    lines = [f'\n```mermaid\nxychart-beta\n  title "{title}"\n  x-axis [']
    lines.append(", ".join(f'"{d}"' for d in dates))
    lines.append("]\n  line [")
    lines.append(", ".join(str(int(v)) for v in values))
    lines.append("]\n```\n")
    return lines


def _monthly_traffic_table(data: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Build a combined monthly traffic table: avg daily uniques/views/unique clones/clones."""
    months: set[str] = set()
    views_uniq: dict[str, list[float]] = defaultdict(list)
    views_cnt: dict[str, list[float]] = defaultdict(list)
    clones_uniq: dict[str, list[float]] = defaultdict(list)
    clones_cnt: dict[str, list[float]] = defaultdict(list)

    for r in data["views"]:
        m = _date_to_month(r["date"])
        months.add(m)
        views_uniq[m].append(float(r["uniques"]))
        views_cnt[m].append(float(r["count"]))
    for r in data["clones"]:
        m = _date_to_month(r["date"])
        months.add(m)
        clones_uniq[m].append(float(r["uniques"]))
        clones_cnt[m].append(float(r["count"]))

    if not months:
        return []

    lines = [
        "\n## Traffic\n\n",
        "| Month | Unique Visitors/day | Views/day | Unique Clones/day | Clones/day |\n",
        "|---|---|---|---|---|\n",
    ]
    for month in sorted(months):
        uv = sum(views_uniq[month]) / len(views_uniq[month]) if views_uniq[month] else 0.0
        v = sum(views_cnt[month]) / len(views_cnt[month]) if views_cnt[month] else 0.0
        uc = sum(clones_uniq[month]) / len(clones_uniq[month]) if clones_uniq[month] else 0.0
        c = sum(clones_cnt[month]) / len(clones_cnt[month]) if clones_cnt[month] else 0.0
        lines.append(f"| {month} | {uv:.1f} | {v:.1f} | {uc:.1f} | {c:.1f} |\n")
    return lines


def _current_totals_pivoted(data: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Build a pivoted current totals table (rows=metrics, single value column)."""
    meta = data["metadata"]
    if not meta:
        return []
    latest = meta[-1]
    lines = [
        "\n## Current Totals\n\n",
        "| Metric | Value |\n",
        "|---|---|\n",
        f"| Stars | {latest.get('stars', '—')} |\n",
        f"| Forks | {latest.get('forks', '—')} |\n",
    ]
    return lines


def _commits_weekly_table(data: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Build a table of the last _COMMITS_TABLE_WEEKS weeks of commits."""
    activity = sorted(data["commit_activity"], key=lambda r: r["week_start"])
    recent = activity[-_COMMITS_TABLE_WEEKS:]
    if not recent:
        return []
    lines = [
        f"\n## Commits per Week (last {_COMMITS_TABLE_WEEKS} weeks)\n\n",
        "| Week | Commits |\n",
        "|---|---|\n",
    ]
    for r in recent:
        lines.append(f"| {r['week_start']} | {r['total']} |\n")
    return lines


def _write_repo_readmes(
    data_repo: Path,
    all_data: dict[tuple[str, str], dict[str, list[dict[str, Any]]]],
) -> None:
    """Write per-repo README files."""
    for (owner, name), data in all_data.items():
        lines: list[str] = [f"# {owner}/{name}\n\n", f"_Last updated: {_now_str()}_\n"]

        # Charts
        views = sorted(data["views"], key=lambda r: r["date"])
        if views:
            lines.extend(
                _mermaid_line(
                    [r["date"] for r in views],
                    [r["uniques"] for r in views],
                    "Unique Visitors per Day",
                )
            )
            lines.extend(
                _mermaid_line(
                    [r["date"] for r in views],
                    [r["count"] for r in views],
                    "Views per Day",
                )
            )

        clones = sorted(data["clones"], key=lambda r: r["date"])
        if clones:
            lines.extend(
                _mermaid_line(
                    [r["date"] for r in clones],
                    [r["uniques"] for r in clones],
                    "Unique Clones per Day",
                )
            )

        # Monthly traffic table
        lines.extend(_monthly_traffic_table(data))

        # Current totals (pivoted)
        lines.extend(_current_totals_pivoted(data))

        # Commits per week
        activity = sorted(data["commit_activity"], key=lambda r: r["week_start"])
        if activity:
            lines.extend(
                _mermaid_line(
                    [r["week_start"] for r in activity],
                    [r["total"] for r in activity],
                    "Commits per Week",
                )
            )
        lines.extend(_commits_weekly_table(data))

        # Release downloads
        if data["releases"]:
            lines.extend(_releases_table(data))

        _atomic_write(data_repo / owner / name / "README.md", "".join(lines))


def _releases_table(data: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Build a release download counts table from the latest snapshot per tag+asset."""
    latest: dict[tuple[str, str], int] = {}
    for r in data["releases"]:
        key = (r["tag"], r["asset"])
        latest[key] = r["download_count"]
    if not latest:
        return []
    lines = ["\n## Release Downloads\n\n", "| Tag | Asset | Downloads |\n", "|---|---|---|\n"]
    for (tag, asset), count in sorted(latest.items()):
        lines.append(f"| {tag} | {asset} | {count:,} |\n")
    return lines
