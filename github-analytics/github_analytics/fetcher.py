"""GitHub API fetcher for all analytics endpoints (async, httpx.AsyncClient)."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from github_analytics._http_utils import TRANSIENT_5XX as _TRANSIENT_5XX
from github_analytics._http_utils import next_link as _next_link
from github_analytics._http_utils import parse_retry_after as _parse_retry_after
from github_analytics.config import RepoId

BASE = "https://api.github.com"
_MAX_ATTEMPTS = 3


def _headers(token: str, accept: str = "application/vnd.github+json") -> dict[str, str]:
    """Build standard GitHub API request headers."""
    return {"Authorization": f"token {token}", "Accept": accept}


async def _get_with_retry(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    url: str,
    headers: dict[str, str],
) -> tuple[httpx.Response, float, float]:
    """HTTP GET with semaphore-bounded concurrency and rate-limit/transient-error retry.

    Retries on:
    - 429 (rate limit): sleeps for retry-after or exponential backoff.
    - 403 with abuse/secondary-rate-limit body: same.
    - 500, 502, 503, 504 (transient server errors): exponential backoff.

    The semaphore wraps only the HTTP round-trip, not retries or compute.

    Returns:
        (response, io_seconds, wait_seconds)
    """
    last_response: httpx.Response | None = None
    total_io = 0.0
    total_wait = 0.0
    for attempt in range(_MAX_ATTEMPTS):
        async with sem:
            t0 = time.perf_counter()
            response = await client.get(url, headers=headers, follow_redirects=True)
            total_io += time.perf_counter() - t0
        last_response = response
        if response.status_code == 429:
            wait = _parse_retry_after(response.headers.get("retry-after", ""), attempt)
            t0 = time.perf_counter()
            await asyncio.sleep(wait)
            total_wait += time.perf_counter() - t0
            continue
        if response.status_code == 403:
            body = response.text.lower()
            retry_after = response.headers.get("retry-after")
            if retry_after or "abuse" in body or "secondary rate" in body:
                wait = _parse_retry_after(retry_after or "", attempt)
                t0 = time.perf_counter()
                await asyncio.sleep(wait)
                total_wait += time.perf_counter() - t0
                continue
        if response.status_code in _TRANSIENT_5XX:
            wait = float(2**attempt)
            t0 = time.perf_counter()
            await asyncio.sleep(wait)
            total_wait += time.perf_counter() - t0
            continue
        return response, total_io, total_wait
    # All attempts were retryable; return the last response so the caller can
    # call raise_for_status() and surface the final error.
    assert last_response is not None  # always true when _MAX_ATTEMPTS >= 1
    return last_response, total_io, total_wait


async def _get(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    url: str,
    token: str,
    accept: str = "application/vnd.github+json",
) -> tuple[Any, float, float]:  # noqa: ANN401
    """GET a single URL, raise on HTTP error, return (parsed JSON, io_s, wait_s)."""
    response, io_s, wait_s = await _get_with_retry(client, sem, url, _headers(token, accept))
    response.raise_for_status()
    return response.json(), io_s, wait_s


async def _paginate(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    url: str,
    token: str,
    accept: str = "application/vnd.github+json",
) -> tuple[list[Any], float, float]:
    """GET all pages of a paginated endpoint.

    Returns:
        (all_results, total_io_seconds, total_wait_seconds)
    """
    results: list[Any] = []
    next_url: str | None = url
    total_io = 0.0
    total_wait = 0.0
    while next_url:
        response, io_s, wait_s = await _get_with_retry(client, sem, next_url, _headers(token, accept))
        response.raise_for_status()
        results.extend(response.json())
        total_io += io_s
        total_wait += wait_s
        next_url = _next_link(response.headers.get("link", ""))
    return results, total_io, total_wait


async def fetch_traffic_views(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Fetch daily traffic views. Returns (records, io_s, wait_s)."""
    data, io_s, wait_s = await _get(
        client, sem, f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/views", token
    )
    records = [
        {"date": v["timestamp"][:10], "count": v["count"], "uniques": v["uniques"]}
        for v in data.get("views", [])
    ]
    return records, io_s, wait_s


async def fetch_traffic_clones(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Fetch daily traffic clones. Returns (records, io_s, wait_s)."""
    data, io_s, wait_s = await _get(
        client, sem, f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/clones", token
    )
    records = [
        {"date": c["timestamp"][:10], "count": c["count"], "uniques": c["uniques"]}
        for c in data.get("clones", [])
    ]
    return records, io_s, wait_s


async def fetch_traffic_referrers(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Fetch top referrers snapshot. Returns (records, io_s, wait_s)."""
    data, io_s, wait_s = await _get(
        client,
        sem,
        f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/popular/referrers",
        token,
    )
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    records = [
        {"date": today, "referrer": r["referrer"], "count": r["count"], "uniques": r["uniques"]} for r in data
    ]
    return records, io_s, wait_s


async def fetch_traffic_paths(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Fetch top paths snapshot. Returns (records, io_s, wait_s)."""
    data, io_s, wait_s = await _get(
        client,
        sem,
        f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/popular/paths",
        token,
    )
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    records = [
        {
            "date": today,
            "path": p["path"],
            "title": p["title"],
            "count": p["count"],
            "uniques": p["uniques"],
        }
        for p in data
    ]
    return records, io_s, wait_s


async def fetch_stars(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Fetch all star events. Returns (records, io_s, wait_s)."""
    items, io_s, wait_s = await _paginate(
        client,
        sem,
        f"{BASE}/repos/{repo['owner']}/{repo['name']}/stargazers?per_page=100",
        token,
        accept="application/vnd.github.v3.star+json",
    )
    records = [{"starred_at": item["starred_at"], "user": item["user"]["login"]} for item in items]
    return records, io_s, wait_s


async def fetch_forks(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Fetch all fork events. Returns (records, io_s, wait_s)."""
    items, io_s, wait_s = await _paginate(
        client, sem, f"{BASE}/repos/{repo['owner']}/{repo['name']}/forks?per_page=100", token
    )
    records = [{"forked_at": item["created_at"], "owner": item["owner"]["login"]} for item in items]
    return records, io_s, wait_s


async def fetch_releases(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Fetch release asset download counts. Returns (records, io_s, wait_s)."""
    releases, io_s, wait_s = await _paginate(
        client, sem, f"{BASE}/repos/{repo['owner']}/{repo['name']}/releases", token
    )
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    records: list[dict[str, Any]] = []
    for release in releases:
        for asset in release.get("assets", []):
            records.append(
                {
                    "date": today,
                    "tag": release["tag_name"],
                    "asset": asset["name"],
                    "download_count": asset["download_count"],
                }
            )
    return records, io_s, wait_s


async def fetch_metadata(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[dict[str, Any], float, float]:
    """Fetch repo metadata snapshot. Returns (record, io_s, wait_s)."""
    data, io_s, wait_s = await _get(client, sem, f"{BASE}/repos/{repo['owner']}/{repo['name']}", token)
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    record = {
        "date": today,
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "watchers": data["watchers_count"],
        "open_issues": data["open_issues_count"],
        "network_count": data.get("network_count"),
        "subscribers": data.get("subscribers_count"),
        "size_kb": data.get("size"),
    }
    return record, io_s, wait_s


async def fetch_metadata_as_list(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Wrap fetch_metadata to return a list for uniform dispatch in the CLI."""
    record, io_s, wait_s = await fetch_metadata(client, sem, repo, token)
    return [record], io_s, wait_s


async def fetch_workflow_runs(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    repo: RepoId,
    token: str,
) -> tuple[list[dict[str, Any]], float, float]:
    """Fetch workflow run aggregates for the last 14 days.

    Paginates through /actions/runs, stopping when runs older than 14 days are reached.
    Groups by (date, name, path, workflow_id, status, conclusion) and stores:
    completed_count, incomplete_count, avg_duration_seconds.
    """
    cutoff = (datetime.now(UTC) - timedelta(days=14)).strftime("%Y-%m-%d")

    all_runs: list[dict[str, Any]] = []
    url: str | None = f"{BASE}/repos/{repo['owner']}/{repo['name']}/actions/runs?per_page=100"
    total_io = 0.0
    total_wait = 0.0
    while url:
        response, io_s, wait_s = await _get_with_retry(client, sem, url, _headers(token))
        response.raise_for_status()
        total_io += io_s
        total_wait += wait_s
        page = response.json()
        runs_on_page = page.get("workflow_runs", [])
        all_runs.extend(runs_on_page)
        # Stop fetching once the last run on the page predates the cutoff.
        # Filter out-of-window runs in a post-pass to handle any out-of-order
        # entries that may appear within a page.
        if runs_on_page and runs_on_page[-1]["created_at"][:10] < cutoff:
            break
        url = _next_link(response.headers.get("link", ""))

    # Keep only runs within the 14-day window
    all_runs = [r for r in all_runs if r["created_at"][:10] >= cutoff]

    # Aggregate by (date, name, path, workflow_id, status, conclusion)
    completed_durations: dict[tuple[str, str, str, int, str, str], list[float]] = defaultdict(list)
    incomplete_counts: dict[tuple[str, str, str, int, str, str], int] = defaultdict(int)

    for run in all_runs:
        date = run["created_at"][:10]
        raw_conclusion = run.get("conclusion")  # None for in-progress runs
        conclusion: str = raw_conclusion or ""  # coerce to str for use as dict key
        key = (date, run["name"], run["path"], run["workflow_id"], run["status"], conclusion)
        if raw_conclusion is not None and run.get("run_started_at") and run.get("updated_at"):
            try:
                started = datetime.fromisoformat(run["run_started_at"].replace("Z", "+00:00"))
                updated = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
                completed_durations[key].append((updated - started).total_seconds())
            except (ValueError, TypeError):
                incomplete_counts[key] += 1
        else:
            incomplete_counts[key] += 1

    all_keys = set(completed_durations) | set(incomplete_counts)
    records: list[dict[str, Any]] = []
    for key in all_keys:
        date, name, path, workflow_id, status, conclusion = key
        durations = completed_durations.get(key, [])
        inc = incomplete_counts.get(key, 0)
        avg_dur: float | None = round(sum(durations) / len(durations), 1) if durations else None
        records.append(
            {
                "date": date,
                "name": name,
                "path": path,
                "workflow_id": workflow_id,
                "status": status,
                "conclusion": conclusion,
                "completed_count": len(durations),
                "incomplete_count": inc,
                "avg_duration_seconds": avg_dur,
            }
        )
    return records, total_io, total_wait
