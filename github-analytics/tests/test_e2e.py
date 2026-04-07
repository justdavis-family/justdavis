"""End-to-end tests: full collect+report pipeline against VCR cassettes.

Tests call cmd_collect() as a Python function (not subprocess)
so that pytest-recording/vcrpy can intercept httpx calls within the test process.
"""

import json
import os
from pathlib import Path

import pytest

from github_analytics.__main__ import cmd_collect


@pytest.fixture()
def data_repo(tmp_path: Path) -> Path:
    """Temporary directory used as the data repository root."""
    return tmp_path / "data-repo"


@pytest.fixture()
def fixture_config() -> Path:
    """Path to the single-repo fixture config."""
    return Path(__file__).parent / "fixtures" / "config_single_repo.yaml"


@pytest.fixture(autouse=True)
def fake_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Inject a token; real value used when recording, fake-token for cassette replay."""
    token = os.environ.get("GITHUB_TOKEN", "fake-token")
    monkeypatch.setenv("GITHUB_TOKEN", token)


@pytest.mark.vcr
def test_collect_creates_ndjson_files(data_repo: Path, fixture_config: Path) -> None:
    """Running collect populates the data repo with NDJSON files."""
    import argparse

    args = argparse.Namespace(
        data_repo=str(data_repo), config=str(fixture_config), max_concurrent=1, verbose=False
    )
    exit_code = cmd_collect(args)
    assert exit_code == 0

    views = data_repo / "karlmdavis" / "ksoap2-android" / "views.ndjson"
    assert views.exists(), f"Expected {views} to exist"
    for line in views.read_text().strip().splitlines():
        record = json.loads(line)
        assert "date" in record
        assert "count" in record


@pytest.mark.vcr
def test_collect_is_idempotent(data_repo: Path, fixture_config: Path) -> None:
    """Running collect twice produces no extra records in any NDJSON file.

    Upsert metrics (views, clones, metadata, referrers, paths, workflow_runs)
    replace existing records on the second run, so line counts stay the same.
    Append-only metrics (stars, forks) skip duplicates, so their line counts
    also stay the same.
    Note: releases idempotency is not exercised here because ksoap2-android
    has no releases; the upsert mechanism for releases is covered by the
    test_writer.py unit tests.
    """
    import argparse

    args = argparse.Namespace(
        data_repo=str(data_repo), config=str(fixture_config), max_concurrent=1, verbose=False
    )
    assert cmd_collect(args) == 0

    repo_dir = data_repo / "karlmdavis" / "ksoap2-android"

    # Record line counts after the first run.
    def _line_counts() -> dict[str, int]:
        return {
            p.name: len([ln for ln in p.read_text().splitlines() if ln.strip()])
            for p in repo_dir.glob("*.ndjson")
        }

    counts_after_first = _line_counts()

    assert cmd_collect(args) == 0  # Second run — cassette replays same responses

    counts_after_second = _line_counts()

    for filename, first_count in counts_after_first.items():
        second_count = counts_after_second[filename]
        assert second_count == first_count, (
            f"{filename}: line count changed from {first_count} to {second_count} on second run"
        )

    # Also verify no duplicate keys exist after the second run.
    views = repo_dir / "views.ndjson"
    assert views.exists(), f"Expected {views} to exist"
    dates = [json.loads(ln)["date"] for ln in views.read_text().splitlines() if ln.strip()]
    assert len(dates) == len(set(dates)), f"views: duplicate date records: {dates}"

    stars = repo_dir / "stars.ndjson"
    if stars.exists():
        keys = [
            (json.loads(ln)["starred_at"], json.loads(ln)["user"])
            for ln in stars.read_text().splitlines()
            if ln.strip()
        ]
        assert len(keys) == len(set(keys)), f"stars: duplicate keys: {keys}"


@pytest.mark.default_cassette("test_collect_creates_ndjson_files.yaml")
@pytest.mark.vcr
def test_report_generates_readmes(data_repo: Path, fixture_config: Path) -> None:
    """Running report after collect creates README files at all three levels."""
    import argparse

    from github_analytics import reporter

    args = argparse.Namespace(
        data_repo=str(data_repo), config=str(fixture_config), max_concurrent=1, verbose=False
    )

    # Collect data first (VCR replays the cassette from the collect test)
    assert cmd_collect(args) == 0

    # Generate reports (reads local files only — no HTTP calls)
    assert reporter.generate(data_repo) == 0

    # Root README must exist
    root = data_repo / "README.md"
    assert root.exists()
    root_content = root.read_text()
    assert "Last updated" in root_content
    assert "# GitHub Analytics" in root_content

    # Per-owner README must exist
    assert (data_repo / "karlmdavis" / "README.md").exists()

    # Per-repo README must exist
    assert (data_repo / "karlmdavis" / "ksoap2-android" / "README.md").exists()
