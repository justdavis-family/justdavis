import os
from pathlib import Path

import pytest

from github_analytics.config import RepoId, load_repos

_TOKEN = os.environ.get("GITHUB_TOKEN", "fake-token")


def test_load_repos_explicit(tmp_path: Path) -> None:
    """Explicit owner/repo entries are returned as-is."""
    config = tmp_path / "config.yaml"
    config.write_text("repos:\n  - karlmdavis/ksoap2-android\n  - justdavis-family/justdavis\n")
    result = load_repos(config, token="unused")
    assert result == [
        RepoId(owner="karlmdavis", name="ksoap2-android"),
        RepoId(owner="justdavis-family", name="justdavis"),
    ]


@pytest.mark.vcr
def test_load_repos_org_wildcard(tmp_path: Path) -> None:
    """org: entries are expanded to all repos in the org."""
    config = tmp_path / "config.yaml"
    config.write_text("repos:\n  - org:justdavis-family\n")
    result = load_repos(config, token=_TOKEN)
    # justdavis-family has at least the justdavis repo
    assert any(r["owner"] == "justdavis-family" for r in result)


@pytest.mark.vcr
def test_load_repos_user_wildcard(tmp_path: Path) -> None:
    """user: entries are expanded to all repos for the user."""
    config = tmp_path / "config.yaml"
    config.write_text("repos:\n  - user:karlmdavis\n")
    result = load_repos(config, token=_TOKEN)
    assert any(r["owner"] == "karlmdavis" for r in result)


def test_load_repos_deduplication(tmp_path: Path) -> None:
    """A repo appearing via wildcard and explicit entry is returned once."""
    config = tmp_path / "config.yaml"
    config.write_text("repos:\n  - justdavis-family/justdavis\n  - justdavis-family/justdavis\n")
    result = load_repos(config, token="unused")
    assert result.count(RepoId(owner="justdavis-family", name="justdavis")) == 1
