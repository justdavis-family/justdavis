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
        #
        # Decompress gzip-encoded API responses before storing them in cassettes.
        # Trade-off: cassette bodies are human-readable JSON instead of base64-encoded binary,
        # at the cost of slightly reduced replay fidelity (the Accept-Encoding negotiation is
        # not replayed). In practice this makes no difference for our tests and dramatically
        # improves the developer experience when reading or diffing cassette files.
        "decode_compressed_response": True,
    }
