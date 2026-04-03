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
    """Build standard GitHub API request headers."""
    return {"Authorization": f"token {token}", "Accept": accept}


def _get_with_retry(url: str, headers: dict[str, str]) -> httpx.Response:
    """HTTP GET with retry for primary (429) and secondary (403 abuse) rate limits."""
    last_response: httpx.Response | None = None
    for attempt in range(_MAX_RETRIES):
        response = httpx.get(url, headers=headers, follow_redirects=True)
        last_response = response
        if response.status_code == 429:
            wait = float(response.headers.get("retry-after", 2**attempt))
            time.sleep(wait)
            continue
        if response.status_code == 403:
            body = response.text.lower()
            retry_after = response.headers.get("retry-after")
            if retry_after or "abuse" in body or "secondary rate" in body:
                wait = float(retry_after or 2**attempt)
                time.sleep(wait)
                continue
        return response
    assert last_response is not None
    return last_response


def _get(url: str, token: str, accept: str = "application/vnd.github+json") -> Any:  # noqa: ANN401
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
    """Parse GitHub's Link header and return the 'next' URL, if any."""
    for part in link_header.split(","):
        url_part, *params = part.strip().split(";")
        if any('rel="next"' in p for p in params):
            return url_part.strip().strip("<>")
    return None


def _now_utc() -> str:
    """Return the current UTC time in ISO 8601 format."""
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
    return [
        {"collected_at": now, "referrer": r["referrer"], "count": r["count"], "uniques": r["uniques"]}
        for r in data
    ]


def fetch_traffic_paths(repo: RepoId, token: str) -> list[dict[str, Any]]:
    """Fetch top paths snapshot. Returns list of {collected_at, path, title, count, uniques}."""
    data = _get(f"{BASE}/repos/{repo['owner']}/{repo['name']}/traffic/popular/paths", token)
    now = _now_utc()
    return [
        {
            "collected_at": now,
            "path": p["path"],
            "title": p["title"],
            "count": p["count"],
            "uniques": p["uniques"],
        }
        for p in data
    ]


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
    """Fetch release asset download counts. Returns list of {collected_at, tag, asset, download_count}."""
    releases = _paginate(f"{BASE}/repos/{repo['owner']}/{repo['name']}/releases", token)
    now = _now_utc()
    records: list[dict[str, Any]] = []
    for release in releases:
        for asset in release.get("assets", []):
            records.append(
                {
                    "collected_at": now,
                    "tag": release["tag_name"],
                    "asset": asset["name"],
                    "download_count": asset["download_count"],
                }
            )
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
