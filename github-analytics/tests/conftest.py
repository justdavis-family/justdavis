import pytest


@pytest.fixture(scope="session")
def vcr_config() -> dict[str, object]:
    """VCR configuration: store cassettes in tests/cassettes/, filter auth headers.

    Must be session-scoped so pytest-recording applies this config globally.
    """
    return {
        "cassette_library_dir": "tests/cassettes",
        "filter_headers": ["authorization"],
        # record_mode omitted: pytest-recording defaults to "none" (fail if cassette missing).
        # Override with --record-mode=new_episodes to record cassettes against the live API.
    }
