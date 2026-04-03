"""Run with --record-mode=new_episodes and GITHUB_TOKEN set to record VCR cassettes.

Usage:
    cd github-analytics
    source .env && GITHUB_TOKEN=$GITHUB_PAT_COLLECTOR \\
      uv run pytest tests/recording_tests.py --record-mode=new_episodes -v

pytest-recording intercepts httpx calls and writes cassettes to tests/cassettes/.
The authorization header is filtered from all cassettes (see conftest.py vcr_config).
"""
import os

import pytest

from github_analytics import fetcher
from github_analytics.config import RepoId, _list_org_repos, _list_user_repos

KSOAP = RepoId(owner="karlmdavis", name="ksoap2-android")
JUSTDAVIS = RepoId(owner="justdavis-family", name="justdavis")


def _token() -> str:
    return os.environ["GITHUB_TOKEN"]


@pytest.mark.vcr("traffic_views.yaml")
def test_record_traffic_views() -> None:
    fetcher.fetch_traffic_views(KSOAP, _token())


@pytest.mark.vcr("traffic_clones.yaml")
def test_record_traffic_clones() -> None:
    fetcher.fetch_traffic_clones(KSOAP, _token())


@pytest.mark.vcr("traffic_referrers.yaml")
def test_record_traffic_referrers() -> None:
    fetcher.fetch_traffic_referrers(KSOAP, _token())


@pytest.mark.vcr("traffic_paths.yaml")
def test_record_traffic_paths() -> None:
    fetcher.fetch_traffic_paths(KSOAP, _token())


@pytest.mark.vcr("stars.yaml")
def test_record_stars() -> None:
    fetcher.fetch_stars(KSOAP, _token())


@pytest.mark.vcr("forks.yaml")
def test_record_forks() -> None:
    fetcher.fetch_forks(KSOAP, _token())


@pytest.mark.vcr("releases.yaml")
def test_record_releases() -> None:
    fetcher.fetch_releases(KSOAP, _token())


@pytest.mark.vcr("metadata.yaml")
def test_record_metadata() -> None:
    fetcher.fetch_metadata(KSOAP, _token())


@pytest.mark.vcr("traffic_views_quiet.yaml")
def test_record_traffic_views_quiet() -> None:
    fetcher.fetch_traffic_views(JUSTDAVIS, _token())


@pytest.mark.vcr("metadata_quiet.yaml")
def test_record_metadata_quiet() -> None:
    fetcher.fetch_metadata(JUSTDAVIS, _token())


@pytest.mark.vcr("org_repos.yaml")
def test_record_org_repos() -> None:
    _list_org_repos("justdavis-family", _token())


@pytest.mark.vcr("user_repos.yaml")
def test_record_user_repos() -> None:
    _list_user_repos("karlmdavis", _token())


@pytest.mark.vcr("e2e_collect.yaml")
def test_record_e2e_collect() -> None:
    """Record all API calls made by a full collect run for one repo."""
    import argparse
    from pathlib import Path

    from github_analytics.__main__ import cmd_collect

    args = argparse.Namespace(
        data_repo="/tmp/e2e-cassette-recording",
        config=str(Path(__file__).parent / "fixtures" / "config_single_repo.yaml"),
    )
    cmd_collect(args)
