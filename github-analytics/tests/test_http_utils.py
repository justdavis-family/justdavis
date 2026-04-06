"""Unit tests for _http_utils shared HTTP utilities."""

from github_analytics._http_utils import next_link, parse_retry_after


def test_parse_retry_after_integer_seconds() -> None:
    assert parse_retry_after("30", attempt=0) == 30.0


def test_parse_retry_after_zero() -> None:
    assert parse_retry_after("0", attempt=0) == 0.0


def test_parse_retry_after_empty_falls_back_to_backoff() -> None:
    assert parse_retry_after("", attempt=0) == 1.0  # 2**0
    assert parse_retry_after("", attempt=1) == 2.0  # 2**1
    assert parse_retry_after("", attempt=2) == 4.0  # 2**2


def test_parse_retry_after_http_date_returns_positive_or_zero(monkeypatch: object) -> None:
    """An RFC 7231 HTTP-date string is parsed; the returned wait is >= 0."""
    import github_analytics._http_utils as mod

    # Freeze time at 0 so the arithmetic is deterministic.
    monkeypatch.setattr(mod, "time", type("T", (), {"time": staticmethod(lambda: 0.0)})())  # type: ignore[arg-type]
    # A date far in the future relative to frozen time=0.
    result = parse_retry_after("Thu, 01 Jan 2099 00:00:00 GMT", attempt=0)
    assert result > 0.0


def test_parse_retry_after_unparseable_falls_back_to_backoff() -> None:
    assert parse_retry_after("not-a-date-or-number", attempt=1) == 2.0


def test_next_link_present() -> None:
    header = (
        '<https://api.github.com/orgs/foo/repos?page=2>; rel="next", '
        '<https://api.github.com/orgs/foo/repos?page=5>; rel="last"'
    )
    assert next_link(header) == "https://api.github.com/orgs/foo/repos?page=2"


def test_next_link_absent() -> None:
    header = '<https://api.github.com/orgs/foo/repos?page=5>; rel="last"'
    assert next_link(header) is None


def test_next_link_empty() -> None:
    assert next_link("") is None
