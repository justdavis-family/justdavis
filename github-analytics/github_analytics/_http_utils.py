"""Shared HTTP utilities for GitHub API pagination and retry-after parsing."""

from __future__ import annotations

# GitHub API transient server-error status codes that warrant a retry.
TRANSIENT_5XX: frozenset[int] = frozenset({500, 502, 503, 504})


def next_link(link_header: str) -> str | None:
    """Parse GitHub's Link header and return the 'next' URL, if any."""
    for part in link_header.split(","):
        url_part, *params = part.strip().split(";")
        if any('rel="next"' in p for p in params):
            return url_part.strip().strip("<>")
    return None


def parse_retry_after(header: str, attempt: int) -> float:
    """Return sleep duration from a Retry-After header value (or exponential backoff).

    The header may be an integer seconds count or an HTTP-date string (RFC 7231).
    Falls back to exponential backoff (2**attempt) if the value cannot be parsed
    as a float, avoiding a ValueError that would escape the retry loop.
    """
    if header:
        try:
            return float(header)
        except ValueError:
            pass  # HTTP-date format or unexpected value — fall through to backoff
    return float(2**attempt)
