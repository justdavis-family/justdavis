"""Unit tests for reporter pure builder functions."""

from __future__ import annotations

from github_analytics.reporter import (
    _current_totals_pivoted,
    _current_totals_table,
    _date_to_quarter,
    _mermaid_line,
    _monthly_traffic_table,
    _releases_table,
)


def test_date_to_quarter_q1() -> None:
    assert _date_to_quarter("2024-01-15") == "2024-Q1"
    assert _date_to_quarter("2024-03-31") == "2024-Q1"


def test_date_to_quarter_q2() -> None:
    assert _date_to_quarter("2024-04-01") == "2024-Q2"
    assert _date_to_quarter("2024-06-30") == "2024-Q2"


def test_date_to_quarter_q3() -> None:
    assert _date_to_quarter("2024-07-01") == "2024-Q3"


def test_date_to_quarter_q4() -> None:
    assert _date_to_quarter("2024-10-01") == "2024-Q4"
    assert _date_to_quarter("2024-12-31") == "2024-Q4"


def test_mermaid_line_empty() -> None:
    assert _mermaid_line([], [], "Title") == []


def test_mermaid_line_basic() -> None:
    result = "".join(_mermaid_line(["2024-01-01", "2024-01-02"], [5, 10], "My Chart"))
    assert 'title "My Chart"' in result
    assert '"2024-01-01"' in result
    assert '"2024-01-02"' in result
    assert "5" in result
    assert "10" in result
    assert "```mermaid" in result


def _make_views(records: list[tuple[str, int, int]]) -> list[dict]:
    return [{"date": d, "count": c, "uniques": u} for d, c, u in records]


def _make_clones(records: list[tuple[str, int, int]]) -> list[dict]:
    return [{"date": d, "count": c, "uniques": u} for d, c, u in records]


_ALL_METRICS = [
    "views",
    "clones",
    "referrers",
    "paths",
    "stars",
    "forks",
    "releases",
    "metadata",
    "workflow_runs",
]


def _empty_repo_data() -> dict:
    return {m: [] for m in _ALL_METRICS}


def test_monthly_traffic_table_empty() -> None:
    data = _empty_repo_data()
    assert _monthly_traffic_table(data) == []


def test_monthly_traffic_table_basic() -> None:
    data = _empty_repo_data()
    data["views"] = _make_views([("2024-01-01", 10, 3), ("2024-01-02", 20, 6)])
    data["clones"] = _make_clones([("2024-01-01", 2, 1)])
    result = "".join(_monthly_traffic_table(data))
    assert "2024-01" in result
    assert "Traffic" in result
    # Unique Visitors/day avg = (3+6)/2 = 4.5
    assert "4.5" in result


def test_current_totals_pivoted_empty() -> None:
    data = _empty_repo_data()
    assert _current_totals_pivoted(data) == []


def test_current_totals_pivoted_uses_latest_date() -> None:
    data = _empty_repo_data()
    # Two records; function should use the one with the latest date
    data["metadata"] = [
        {"date": "2024-01-01", "stars": 5, "forks": 1},
        {"date": "2024-02-01", "stars": 10, "forks": 2},
    ]
    result = "".join(_current_totals_pivoted(data))
    assert "| Stars | 10 |" in result
    assert "| Forks | 2 |" in result


def test_current_totals_table_uses_latest_date() -> None:
    base = {m: [] for m in _ALL_METRICS}
    all_data = {
        ("owner", "repo"): {
            **base,
            "metadata": [
                {"date": "2024-01-01", "stars": 5, "forks": 1},
                {"date": "2024-03-01", "stars": 20, "forks": 4},
            ],
        }
    }
    result = "".join(_current_totals_table(all_data))
    assert "| owner/repo | 20 | 4 |" in result


def test_current_totals_table_missing_metadata() -> None:
    all_data = {("owner", "repo"): _empty_repo_data()}
    result = "".join(_current_totals_table(all_data))
    assert "owner/repo" in result
    assert "—" in result


def test_releases_table_empty() -> None:
    data = _empty_repo_data()
    assert _releases_table(data) == []


def test_releases_table_uses_latest_per_tag_asset() -> None:
    data = _empty_repo_data()
    data["releases"] = [
        {"date": "2024-01-01", "tag": "v1.0", "asset": "app.zip", "download_count": 50},
        {"date": "2024-02-01", "tag": "v1.0", "asset": "app.zip", "download_count": 75},
    ]
    result = "".join(_releases_table(data))
    assert "v1.0" in result
    assert "app.zip" in result
    # Should use the last-seen download_count (75), not the first (50)
    assert "75" in result
    assert "50" not in result


def test_releases_table_sorts_by_release_creation_date() -> None:
    """Rows are ordered by release_created_at newest-first."""
    data = _empty_repo_data()
    data["releases"] = [
        {
            "date": "2024-01-01",
            "tag": "v1.0",
            "release_created_at": "2024-01-01T00:00:00Z",
            "asset": "app.zip",
            "download_count": 10,
        },
        {
            "date": "2024-02-01",
            "tag": "v2.0",
            "release_created_at": "2024-02-01T00:00:00Z",
            "asset": "app.zip",
            "download_count": 20,
        },
    ]
    result = "".join(_releases_table(data))
    # v2.0 (newer release_created_at) should appear before v1.0 (older)
    assert result.index("v2.0") < result.index("v1.0")
