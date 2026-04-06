"""Shared HTTP utilities for GitHub API pagination and retry-after parsing."""

from __future__ import annotations

import time
from email.utils import parsedate_to_datetime

# Maximum number of retry attempts for rate-limited or transient-error requests.
MAX_ATTEMPTS: int = 3

# GitHub API transient server-error status codes that warrant a retry.
TRANSIENT_5XX: frozenset[int] = frozenset({500, 502, 503, 504})


def next_link(link_header: str) -> str | None:
    """Parse GitHub's Link header and return the 'next' URL, if any.

    Splits on commas before inspecting individual link entries. This is safe
    for GitHub's pagination URLs, which never contain commas. A full RFC 8288
    parser would find ``<...>`` brackets first, but that complexity is not
    warranted here.
    """
    for part in link_header.split(","):
        url_part, *params = part.strip().split(";")
        if any('rel="next"' in p for p in params):
            return url_part.strip().strip("<>")
    return None


def parse_retry_after(header: str, attempt: int) -> float:
    """Return sleep duration from a Retry-After header value (or exponential backoff).

    GitHub's Retry-After header may be either an integer seconds count or an
    RFC 7231 HTTP-date string (e.g. ``Fri, 07 Apr 2026 00:00:00 GMT``).
    Falls back to exponential backoff (2**attempt) if the value cannot be parsed.
    """
    if header:
        try:
            return float(header)
        except ValueError:
            pass
        try:
            dt = parsedate_to_datetime(header)
            return max(0.0, dt.timestamp() - time.time())
        except Exception:
            pass
    return float(2**attempt)
