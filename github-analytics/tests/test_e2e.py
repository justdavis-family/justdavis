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

    args = argparse.Namespace(data_repo=str(data_repo), config=str(fixture_config))
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
    """Running collect twice on the same day produces no duplicate records."""
    import argparse

    args = argparse.Namespace(data_repo=str(data_repo), config=str(fixture_config))
    cmd_collect(args)
    cmd_collect(args)  # Second run — cassette replays same responses

    views = data_repo / "karlmdavis" / "ksoap2-android" / "views.ndjson"
    if views.exists():
        lines = views.read_text().strip().splitlines()
        dates = [json.loads(line)["date"] for line in lines if line.strip()]
        assert len(dates) == len(set(dates)), f"Duplicate date records: {dates}"


@pytest.mark.default_cassette("test_collect_creates_ndjson_files.yaml")
@pytest.mark.vcr
def test_report_generates_readmes(data_repo: Path, fixture_config: Path) -> None:
    """Running report after collect creates README files at all three levels."""
    import argparse

    from github_analytics import reporter

    args = argparse.Namespace(data_repo=str(data_repo), config=str(fixture_config))

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
