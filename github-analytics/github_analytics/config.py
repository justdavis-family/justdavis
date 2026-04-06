"""Config loading: parse config.yaml and expand repo patterns."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, TypedDict

import httpx
import yaml

from github_analytics._http_utils import MAX_ATTEMPTS as _MAX_ATTEMPTS
from github_analytics._http_utils import TRANSIENT_5XX as _TRANSIENT_5XX
from github_analytics._http_utils import next_link as _next_link
from github_analytics._http_utils import parse_retry_after as _parse_retry_after


class RepoId(TypedDict):
    """Identifies a GitHub repository."""

    owner: str
    name: str


def load_repos(config_path: Path, token: str) -> list[RepoId]:
    """Load and expand the repository list from config.yaml.

    Expands ``org:<name>`` and ``user:<name>`` patterns via the GitHub API.
    Deduplicates the result.

    Note: uses synchronous HTTP (httpx.get). Must be called before entering
    an asyncio event loop — calling from inside ``async def`` will block the loop.
    """
    with config_path.open(encoding="utf-8") as f:
        raw: Any = yaml.safe_load(f)

    patterns: list[str] = raw.get("repos") or []
    repos: list[RepoId] = []
    seen: set[tuple[str, str]] = set()

    for pattern in patterns:
        for repo in _expand_pattern(pattern, token):
            key = (repo["owner"], repo["name"])
            if key not in seen:
                seen.add(key)
                repos.append(repo)
    return repos


def _expand_pattern(pattern: str, token: str) -> list[RepoId]:
    """Expand a single pattern to a list of RepoIds."""
    if pattern.startswith("org:"):
        org = pattern[4:]
        return _list_org_repos(org, token)
    if pattern.startswith("user:"):
        user = pattern[5:]
        return _list_user_repos(user, token)
    # Explicit owner/repo
    if "/" not in pattern:
        raise ValueError(
            f"Invalid repo pattern {pattern!r}: expected 'owner/name', 'org:<name>', or 'user:<name>'"
        )
    owner, name = pattern.split("/", 1)
    return [RepoId(owner=owner, name=name)]


def _list_org_repos(org: str, token: str) -> list[RepoId]:
    """List all repos for a GitHub org via the API."""
    return _paginate(f"https://api.github.com/orgs/{org}/repos?per_page=100", token)


def _list_user_repos(user: str, token: str) -> list[RepoId]:
    """List all repos for a GitHub user via the API."""
    return _paginate(f"https://api.github.com/users/{user}/repos?per_page=100", token)


def _paginate(url: str, token: str) -> list[RepoId]:
    """Fetch all pages of a paginated GitHub API endpoint.

    Retries on 429, 403-abuse, and transient 5xx errors with exponential backoff.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    repos: list[RepoId] = []
    next_url: str | None = url
    while next_url:
        response = _get_with_retry(next_url, headers)
        response.raise_for_status()
        for item in response.json():
            repos.append(RepoId(owner=item["owner"]["login"], name=item["name"]))
        next_url = _next_link(response.headers.get("link", ""))
    return repos


def _get_with_retry(url: str, headers: dict[str, str]) -> httpx.Response:
    """Synchronous GET with retry on rate-limit and transient server errors."""
    last: httpx.Response | None = None
    for attempt in range(_MAX_ATTEMPTS):
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=30.0)
        last = response
        if response.status_code == 429:
            wait = _parse_retry_after(response.headers.get("retry-after", ""), attempt)
            time.sleep(wait)
            continue
        if response.status_code == 403:
            body = response.text.lower()
            retry_after = response.headers.get("retry-after")
            if retry_after or "abuse" in body or "secondary rate" in body:
                wait = _parse_retry_after(retry_after or "", attempt)
                time.sleep(wait)
                continue
        if response.status_code in _TRANSIENT_5XX:
            time.sleep(float(2**attempt))
            continue
        return response
    assert last is not None  # always true when _MAX_ATTEMPTS >= 1
    return last
