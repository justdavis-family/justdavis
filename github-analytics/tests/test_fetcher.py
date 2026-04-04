import os

import pytest

from github_analytics.config import RepoId
from github_analytics.fetcher import (
    fetch_code_frequency,
    fetch_commit_activity,
    fetch_contributors,
    fetch_forks,
    fetch_metadata,
    fetch_metadata_as_list,
    fetch_participation,
    fetch_punch_card,
    fetch_releases,
    fetch_stars,
    fetch_traffic_clones,
    fetch_traffic_paths,
    fetch_traffic_referrers,
    fetch_traffic_views,
    fetch_workflow_runs,
)

TOKEN = os.environ.get("GITHUB_TOKEN", "fake-token")
KSOAP = RepoId(owner="karlmdavis", name="ksoap2-android")


@pytest.mark.vcr
def test_fetch_traffic_views_returns_records() -> None:
    records = fetch_traffic_views(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "date" in r
        assert "count" in r
        assert "uniques" in r


@pytest.mark.vcr
def test_fetch_traffic_clones_returns_records() -> None:
    records = fetch_traffic_clones(KSOAP, TOKEN)
    assert isinstance(records, list)


@pytest.mark.vcr
def test_fetch_traffic_referrers_returns_records() -> None:
    records = fetch_traffic_referrers(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "collected_at" in r
        assert "referrer" in r
        assert "count" in r
        assert "uniques" in r


@pytest.mark.vcr
def test_fetch_traffic_paths_returns_records() -> None:
    records = fetch_traffic_paths(KSOAP, TOKEN)
    assert isinstance(records, list)


@pytest.mark.vcr
def test_fetch_stars_returns_records() -> None:
    records = fetch_stars(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "starred_at" in r
        assert "user" in r


@pytest.mark.vcr
def test_fetch_forks_returns_records() -> None:
    records = fetch_forks(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "forked_at" in r
        assert "owner" in r


@pytest.mark.vcr
def test_fetch_releases_returns_records() -> None:
    records = fetch_releases(KSOAP, TOKEN)
    assert isinstance(records, list)


@pytest.mark.vcr
def test_fetch_metadata_returns_record() -> None:
    record = fetch_metadata(KSOAP, TOKEN)
    assert "date" in record
    assert "stars" in record
    assert "forks" in record
    assert "watchers" in record
    assert "open_issues" in record


def test_fetch_metadata_as_list_wraps_metadata() -> None:
    """fetch_metadata_as_list returns a single-element list; no HTTP call needed."""
    from unittest.mock import patch

    fake_record = {
        "date": "2026-04-03",
        "stars": 10,
        "forks": 5,
        "watchers": 10,
        "open_issues": 2,
        "network_count": 5,
        "subscribers": 3,
        "size_kb": 1024,
    }

    with patch("github_analytics.fetcher.fetch_metadata", return_value=fake_record):
        result = fetch_metadata_as_list(KSOAP, TOKEN)
    assert result == [fake_record]


@pytest.mark.vcr
def test_fetch_commit_activity_returns_records() -> None:
    records = fetch_commit_activity(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "week_start" in r
        assert "total" in r
        assert "days" in r
        assert len(r["days"]) == 7


@pytest.mark.vcr
def test_fetch_code_frequency_returns_records() -> None:
    records = fetch_code_frequency(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "week_start" in r
        assert "additions" in r
        assert "deletions" in r


@pytest.mark.vcr
def test_fetch_contributors_returns_records() -> None:
    records = fetch_contributors(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "week_start" in r
        assert "author" in r
        assert "commits" in r


@pytest.mark.vcr
def test_fetch_participation_returns_records() -> None:
    records = fetch_participation(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "week_start" in r
        assert "all" in r
        assert "owner" in r


@pytest.mark.vcr
def test_fetch_punch_card_returns_records() -> None:
    records = fetch_punch_card(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "day_of_week" in r
        assert "hour" in r
        assert "commits" in r


@pytest.mark.vcr
def test_fetch_workflow_runs_returns_records() -> None:
    records = fetch_workflow_runs(KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "date" in r
        assert "name" in r
        assert "status" in r
        assert "completed_count" in r
        assert "incomplete_count" in r
