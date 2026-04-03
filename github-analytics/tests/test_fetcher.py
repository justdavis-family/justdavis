import pytest

from github_analytics.config import RepoId
from github_analytics.fetcher import (
    fetch_forks,
    fetch_metadata,
    fetch_metadata_as_list,
    fetch_releases,
    fetch_stars,
    fetch_traffic_clones,
    fetch_traffic_paths,
    fetch_traffic_referrers,
    fetch_traffic_views,
)

import os

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
    # This test verifies the wrapper behavior using a small inline fixture
    from unittest.mock import patch

    fake_record = {"date": "2026-04-03", "stars": 10, "forks": 5, "watchers": 10, "open_issues": 2}

    with patch("github_analytics.fetcher.fetch_metadata", return_value=fake_record):
        result = fetch_metadata_as_list(KSOAP, TOKEN)
    assert result == [fake_record]
