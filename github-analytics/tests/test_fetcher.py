import asyncio
import os
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from github_analytics.config import RepoId
from github_analytics.fetcher import (
    _get_with_retry,
    fetch_forks,
    fetch_metadata,
    fetch_metadata_as_list,
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
async def test_fetch_traffic_views_returns_records() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        records, _, _ = await fetch_traffic_views(client, sem, KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "date" in r
        assert "count" in r
        assert "uniques" in r


@pytest.mark.vcr
async def test_fetch_traffic_clones_returns_records() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        records, _, _ = await fetch_traffic_clones(client, sem, KSOAP, TOKEN)
    assert isinstance(records, list)


@pytest.mark.vcr
async def test_fetch_traffic_referrers_returns_records() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        records, _, _ = await fetch_traffic_referrers(client, sem, KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "collected_at" in r
        assert "referrer" in r
        assert "count" in r
        assert "uniques" in r


@pytest.mark.vcr
async def test_fetch_traffic_paths_returns_records() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        records, _, _ = await fetch_traffic_paths(client, sem, KSOAP, TOKEN)
    assert isinstance(records, list)


@pytest.mark.vcr
async def test_fetch_stars_returns_records() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        records, _, _ = await fetch_stars(client, sem, KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "starred_at" in r
        assert "user" in r


@pytest.mark.vcr
async def test_fetch_forks_returns_records() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        records, _, _ = await fetch_forks(client, sem, KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "forked_at" in r
        assert "owner" in r


@pytest.mark.vcr
async def test_fetch_releases_returns_records() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        records, _, _ = await fetch_releases(client, sem, KSOAP, TOKEN)
    assert isinstance(records, list)


@pytest.mark.vcr
async def test_fetch_metadata_returns_record() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        record, _, _ = await fetch_metadata(client, sem, KSOAP, TOKEN)
    assert "date" in record
    assert "stars" in record
    assert "forks" in record
    assert "watchers" in record
    assert "open_issues" in record


async def test_fetch_metadata_as_list_wraps_metadata() -> None:
    """fetch_metadata_as_list returns a single-element list; no HTTP call needed."""
    from unittest.mock import AsyncMock, patch

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

    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        with patch(
            "github_analytics.fetcher.fetch_metadata",
            new_callable=AsyncMock,
            return_value=(fake_record, 0.0, 0.0),
        ):
            result, _, _ = await fetch_metadata_as_list(client, sem, KSOAP, TOKEN)
    assert result == [fake_record]


@pytest.mark.vcr
async def test_fetch_workflow_runs_returns_records() -> None:
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        records, _, _ = await fetch_workflow_runs(client, sem, KSOAP, TOKEN)
    assert isinstance(records, list)
    if records:
        r = records[0]
        assert "date" in r
        assert "name" in r
        assert "status" in r
        assert "completed_count" in r
        assert "incomplete_count" in r


async def test_get_with_retry_retries_on_429() -> None:
    """A 429 response triggers a sleep and a second attempt."""
    call_count = 0
    fake_req = httpx.Request("GET", "https://api.github.com/test")

    async def fake_get(url: str, *, headers: dict, follow_redirects: bool) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            r = httpx.Response(429, headers={"retry-after": "0"}, text="rate limited")
        else:
            r = httpx.Response(200, content=b'{"ok": true}')
        r.request = fake_req  # type: ignore[assignment]
        return r

    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        with patch.object(client, "get", fake_get):
            with patch("asyncio.sleep") as mock_sleep:
                resp, _io_s, wait_s = await _get_with_retry(
                    client, sem, "https://api.github.com/test", {"Authorization": "token fake"}
                )

    assert call_count == 2, "expected one retry after the 429"
    assert resp.status_code == 200
    mock_sleep.assert_called_once_with(0.0)
    assert wait_s > 0


async def test_collect_metric_isolates_fetch_errors(tmp_path: Path) -> None:
    """An exception raised by the fetch function is caught and returned as an error."""
    from github_analytics.__main__ import _collect_metric, _Timing  # noqa: PLC0415

    timings: dict[str, _Timing] = defaultdict(_Timing)

    async def exploding_fetch(
        client: httpx.AsyncClient,
        sem: asyncio.Semaphore,
        repo: RepoId,
        token: str,
    ) -> tuple[list, float, float]:
        raise RuntimeError("injected failure")

    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(1)
        result = await _collect_metric(
            client,
            sem,
            RepoId(owner="test", name="repo"),
            "views",
            exploding_fetch,
            ["date"],
            tmp_path,
            timings,
            "fake-token",
        )

    assert result.error == "injected failure"
    assert result.count == 0
