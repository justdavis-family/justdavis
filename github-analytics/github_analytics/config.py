"""Config loading: parse config.yaml and expand repo patterns."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

import httpx
import yaml


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
    return _paginate(f"https://api.github.com/orgs/{org}/repos", token)


def _list_user_repos(user: str, token: str) -> list[RepoId]:
    """List all repos for a GitHub user via the API."""
    return _paginate(f"https://api.github.com/users/{user}/repos", token)


def _paginate(url: str, token: str) -> list[RepoId]:
    """Fetch all pages of a paginated GitHub API endpoint."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    repos: list[RepoId] = []
    next_url: str | None = url
    while next_url:
        response = httpx.get(next_url, headers=headers, follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        for item in response.json():
            repos.append(RepoId(owner=item["owner"]["login"], name=item["name"]))
        next_url = _next_link(response.headers.get("link", ""))
    return repos


def _next_link(link_header: str) -> str | None:
    """Parse GitHub's Link header and return the 'next' URL, if any."""
    for part in link_header.split(","):
        url_part, *params = part.strip().split(";")
        if any('rel="next"' in p for p in params):
            return url_part.strip().strip("<>")
    return None
