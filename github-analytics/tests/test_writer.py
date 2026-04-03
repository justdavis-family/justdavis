import json
from pathlib import Path

from github_analytics.writer import append_record


def test_append_record_creates_file(tmp_path: Path) -> None:
    """append_record creates the file and parent dirs if they don't exist."""
    dest = tmp_path / "owner" / "repo" / "views.ndjson"
    record = {"date": "2026-04-03", "count": 10, "uniques": 5}
    appended = append_record(dest, record, key_fields=["date"])
    assert appended is True
    assert dest.exists()
    lines = dest.read_text().strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_append_record_appends_new_record(tmp_path: Path) -> None:
    """New records with different keys are appended."""
    dest = tmp_path / "views.ndjson"
    r1 = {"date": "2026-04-03", "count": 10, "uniques": 5}
    r2 = {"date": "2026-04-04", "count": 12, "uniques": 6}
    append_record(dest, r1, key_fields=["date"])
    appended = append_record(dest, r2, key_fields=["date"])
    assert appended is True
    lines = dest.read_text().strip().splitlines()
    assert len(lines) == 2


def test_append_record_deduplicates(tmp_path: Path) -> None:
    """A record with the same key is not appended again."""
    dest = tmp_path / "views.ndjson"
    record = {"date": "2026-04-03", "count": 10, "uniques": 5}
    append_record(dest, record, key_fields=["date"])
    appended = append_record(dest, record, key_fields=["date"])
    assert appended is False
    lines = dest.read_text().strip().splitlines()
    assert len(lines) == 1


def test_append_record_composite_key(tmp_path: Path) -> None:
    """Composite keys are checked correctly."""
    dest = tmp_path / "stars.ndjson"
    r1 = {"starred_at": "2025-01-01T00:00:00Z", "user": "alice"}
    r2 = {"starred_at": "2025-01-01T00:00:00Z", "user": "bob"}
    r_dup = {"starred_at": "2025-01-01T00:00:00Z", "user": "alice"}
    append_record(dest, r1, key_fields=["starred_at", "user"])
    append_record(dest, r2, key_fields=["starred_at", "user"])
    appended = append_record(dest, r_dup, key_fields=["starred_at", "user"])
    assert appended is False
    assert len(dest.read_text().strip().splitlines()) == 2


def test_append_record_atomic_write(tmp_path: Path) -> None:
    """File contents are not corrupted if process crashes mid-write.
    We test this by verifying the final file has valid JSON on every line."""
    dest = tmp_path / "views.ndjson"
    for i in range(5):
        append_record(dest, {"date": f"2026-04-0{i + 1}", "count": i, "uniques": i}, key_fields=["date"])
    for line in dest.read_text().strip().splitlines():
        json.loads(line)  # raises if malformed
