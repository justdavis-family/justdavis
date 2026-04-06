import json
from pathlib import Path

from github_analytics.writer import append_record, append_records


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


def test_append_records_creates_file(tmp_path: Path) -> None:
    """append_records creates the file and parent dirs when they don't exist."""
    dest = tmp_path / "owner" / "repo" / "contributors.ndjson"
    records = [
        {"week_start": "2026-01-01", "author": "alice", "commits": 3},
        {"week_start": "2026-01-08", "author": "alice", "commits": 5},
    ]
    count = append_records(dest, records, key_fields=["week_start", "author"])
    assert count == 2
    assert dest.exists()
    lines = dest.read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == records[0]
    assert json.loads(lines[1]) == records[1]


def test_append_records_appends_to_existing_file(tmp_path: Path) -> None:
    """New records are appended after existing content."""
    dest = tmp_path / "contributors.ndjson"
    existing = {"week_start": "2026-01-01", "author": "alice", "commits": 3}
    append_record(dest, existing, key_fields=["week_start", "author"])
    new_records = [
        {"week_start": "2026-01-08", "author": "alice", "commits": 5},
        {"week_start": "2026-01-15", "author": "alice", "commits": 2},
    ]
    count = append_records(dest, new_records, key_fields=["week_start", "author"])
    assert count == 2
    lines = dest.read_text().strip().splitlines()
    assert len(lines) == 3


def test_append_records_skips_duplicates_in_file(tmp_path: Path) -> None:
    """Records whose keys already exist in the file are not appended."""
    dest = tmp_path / "contributors.ndjson"
    existing = {"week_start": "2026-01-01", "author": "alice", "commits": 3}
    append_record(dest, existing, key_fields=["week_start", "author"])
    count = append_records(dest, [existing], key_fields=["week_start", "author"])
    assert count == 0
    assert len(dest.read_text().strip().splitlines()) == 1


def test_append_records_skips_duplicates_within_batch(tmp_path: Path) -> None:
    """Duplicate keys within the incoming batch are written only once."""
    dest = tmp_path / "contributors.ndjson"
    record = {"week_start": "2026-01-01", "author": "alice", "commits": 3}
    count = append_records(dest, [record, record], key_fields=["week_start", "author"])
    assert count == 1
    assert len(dest.read_text().strip().splitlines()) == 1


def test_append_records_returns_zero_for_empty_input(tmp_path: Path) -> None:
    """Empty records list returns 0 and does not create or modify the file."""
    dest = tmp_path / "contributors.ndjson"
    count = append_records(dest, [], key_fields=["week_start", "author"])
    assert count == 0
    assert not dest.exists()


def test_append_record_tolerates_missing_trailing_newline(tmp_path: Path) -> None:
    """append_record produces valid NDJSON even if the file lacks a trailing newline."""
    dest = tmp_path / "views.ndjson"
    # Write a file that deliberately omits the trailing newline
    dest.write_text('{"date":"2026-04-03","count":10,"uniques":5}')
    append_record(dest, {"date": "2026-04-04", "count": 12, "uniques": 6}, key_fields=["date"])
    lines = [ln for ln in dest.read_text().splitlines() if ln.strip()]
    assert len(lines) == 2
    assert json.loads(lines[0])["date"] == "2026-04-03"
    assert json.loads(lines[1])["date"] == "2026-04-04"


def test_append_records_tolerates_missing_trailing_newline(tmp_path: Path) -> None:
    """append_records produces valid NDJSON even if the file lacks a trailing newline."""
    dest = tmp_path / "views.ndjson"
    dest.write_text('{"date":"2026-04-03","count":10,"uniques":5}')
    count = append_records(
        dest,
        [{"date": "2026-04-04", "count": 12, "uniques": 6}],
        key_fields=["date"],
    )
    assert count == 1
    lines = [ln for ln in dest.read_text().splitlines() if ln.strip()]
    assert len(lines) == 2
    assert json.loads(lines[0])["date"] == "2026-04-03"
    assert json.loads(lines[1])["date"] == "2026-04-04"
