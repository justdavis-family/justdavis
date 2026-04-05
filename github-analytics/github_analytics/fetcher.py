"""GitHub API fetcher for all analytics endpoints."""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from github_analytics.config import RepoId

BASE = "https://api.github.com"
_MAX_RETRIES = 3
# GitHub stats endpoints return 202 while computing results asynchronously.
# Polling every 5 s for up to 60 s covers most repos; cold repos can take 30+ s.
_STATS_POLL_INTERVAL = 5
_STATS_MAX_ATTEMPTS = 60  # 5-minute ceiling at _STATS_POLL_INTERVAL seconds per attempt


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
    """Fetch repo metadata snapshot with all available point-in-time counts."""
    data = _get(f"{BASE}/repos/{repo['owner']}/{repo['name']}", token)
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    return {
        "date": today,
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "watchers": data["watchers_count"],
        "open_issues": data["open_issues_count"],
        "network_count": data.get("network_count"),
        "subscribers": data.get("subscribers_count"),
        "size_kb": data.get("size"),
    }


def fetch_metadata_as_list(repo: RepoId, token: str) -> list[dict[str, Any]]:
    """Wrap fetch_metadata to return a list for uniform dispatch in the CLI."""
    return [fetch_metadata(repo, token)]


def _get_stats(url: str, token: str) -> Any:  # noqa: ANN401
    """GET a stats endpoint, polling on 202 until data is ready or timeout is reached.

    GitHub computes stats asynchronously; the first request (or a request after a
    period of inactivity) returns 202. Subsequent requests return 200 once the data
    is ready, typically within a few seconds but up to several minutes for cold repos.

    Returns [] for repos with no data (empty body) or unsupported endpoints (422).
    Raises RuntimeError if still 202 after _STATS_MAX_ATTEMPTS attempts.
    """
    for attempt in range(_STATS_MAX_ATTEMPTS):
        response = _get_with_retry(url, _headers(token))
        if response.status_code == 202:
            if attempt < _STATS_MAX_ATTEMPTS - 1:
                time.sleep(_STATS_POLL_INTERVAL)
            continue
        if response.status_code == 422:
            # Some endpoints (e.g. code_frequency) are unsupported for forked repos.
            return []
        response.raise_for_status()
        body = response.text.strip()
        if not body:
            # GitHub returns an empty body (not []) for repos with no activity.
            return []
        return response.json()
    raise RuntimeError(
        f"Stats endpoint still returning 202 after {_STATS_MAX_ATTEMPTS} attempts "
        f"({_STATS_MAX_ATTEMPTS * _STATS_POLL_INTERVAL}s): {url}"
    )


def _unix_to_date(ts: int) -> str:
    """Convert a Unix timestamp to an ISO 8601 date string (UTC)."""
    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d")


def fetch_commit_activity(repo: RepoId, token: str) -> list[dict[str, Any]]:
    """Fetch weekly commit activity for the last 52 weeks.

    Returns list of {week_start, total, days} where days is a 7-element list
    [Sun, Mon, Tue, Wed, Thu, Fri, Sat].
    """
    data = _get_stats(f"{BASE}/repos/{repo['owner']}/{repo['name']}/stats/commit_activity", token)
    if not data:
        return []
    return [
        {"week_start": _unix_to_date(entry["week"]), "total": entry["total"], "days": entry["days"]}
        for entry in data
    ]


def fetch_code_frequency(repo: RepoId, token: str) -> list[dict[str, Any]]:
    """Fetch weekly additions and deletions since repo creation.

    Returns list of {week_start, additions, deletions}.
    """
    data = _get_stats(f"{BASE}/repos/{repo['owner']}/{repo['name']}/stats/code_frequency", token)
    if not data:
        return []
    return [
        {"week_start": _unix_to_date(entry[0]), "additions": entry[1], "deletions": entry[2]}
        for entry in data
    ]


def fetch_contributors(repo: RepoId, token: str) -> list[dict[str, Any]]:
    """Fetch per-contributor weekly commit, addition, and deletion counts.

    Returns list of {week_start, author, additions, deletions, commits}.
    """
    data = _get_stats(f"{BASE}/repos/{repo['owner']}/{repo['name']}/stats/contributors", token)
    if not data:
        return []
    records: list[dict[str, Any]] = []
    for contributor in data:
        author = contributor["author"]["login"]
        for week in contributor["weeks"]:
            records.append(
                {
                    "week_start": _unix_to_date(week["w"]),
                    "author": author,
                    "additions": week["a"],
                    "deletions": week["d"],
                    "commits": week["c"],
                }
            )
    return records


def fetch_participation(repo: RepoId, token: str) -> list[dict[str, Any]]:
    """Fetch weekly commit counts (all contributors vs. owner) for the last 52 weeks.

    Returns list of {week_start, all, owner}.
    """
    data = _get_stats(f"{BASE}/repos/{repo['owner']}/{repo['name']}/stats/participation", token)
    if not data:
        return []
    all_counts: list[int] = data.get("all", [])
    owner_counts: list[int] = data.get("owner", [])
    n = len(all_counts)
    if n == 0:
        return []
    # GitHub returns the oldest week first; the last entry is the most recent week.
    # Compute week_start dates by going back from the current Sunday.
    today = datetime.now(UTC)
    days_since_sunday = (today.weekday() + 1) % 7
    most_recent_sunday = today - timedelta(days=days_since_sunday)
    records = []
    for i, (all_c, owner_c) in enumerate(zip(all_counts, owner_counts)):
        weeks_ago = n - 1 - i
        week_start = (most_recent_sunday - timedelta(weeks=weeks_ago)).strftime("%Y-%m-%d")
        records.append({"week_start": week_start, "all": all_c, "owner": owner_c})
    return records


def fetch_punch_card(repo: RepoId, token: str) -> list[dict[str, Any]]:
    """Fetch commit counts by hour of day and day of week (all-time snapshot).

    Returns list of {day_of_week, hour, commits} where day_of_week is 0=Sun..6=Sat.
    """
    data = _get_stats(f"{BASE}/repos/{repo['owner']}/{repo['name']}/stats/punch_card", token)
    if not data:
        return []
    return [{"day_of_week": entry[0], "hour": entry[1], "commits": entry[2]} for entry in data]


def fetch_workflow_runs(repo: RepoId, token: str) -> list[dict[str, Any]]:
    """Fetch workflow run aggregates for the last 14 days.

    Paginates through /actions/runs, stopping when runs older than 14 days are reached.
    Groups by (date, name, path, workflow_id, status, conclusion) and stores:
    completed_count, incomplete_count, avg_duration_seconds.
    """
    cutoff = (datetime.now(UTC) - timedelta(days=14)).strftime("%Y-%m-%d")

    all_runs: list[dict[str, Any]] = []
    url: str | None = f"{BASE}/repos/{repo['owner']}/{repo['name']}/actions/runs?per_page=100"
    done = False
    while url and not done:
        response = _get_with_retry(url, _headers(token))
        response.raise_for_status()
        page = response.json()
        for run in page.get("workflow_runs", []):
            if run["created_at"][:10] < cutoff:
                done = True
                break
            all_runs.append(run)
        if not done:
            url = _next_link(response.headers.get("link", ""))
        else:
            url = None

    # Aggregate by (date, name, path, workflow_id, status, conclusion)
    completed_durations: dict[tuple[str, str, str, int, str, str], list[float]] = defaultdict(list)
    incomplete_counts: dict[tuple[str, str, str, int, str, str], int] = defaultdict(int)

    for run in all_runs:
        date = run["created_at"][:10]
        conclusion: str = run.get("conclusion") or ""
        key = (date, run["name"], run["path"], run["workflow_id"], run["status"], conclusion)
        if conclusion and run.get("run_started_at") and run.get("updated_at"):
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
    return records
