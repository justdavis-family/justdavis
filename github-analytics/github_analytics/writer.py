"""NDJSON writer with idempotent append/upsert and atomic file writes."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def append_record(
    file_path: Path,
    record: dict[str, Any],
    key_fields: list[str],
    *,
    upsert: bool = False,
) -> bool:
    """Append ``record`` to ``file_path`` unless a matching key already exists.

    When ``upsert=True``, an existing record with the same key is replaced
    rather than skipped.

    Creates the file (and parent directories) if they don't exist.
    Uses atomic temp-file-then-rename to avoid partial writes.

    Returns:
        True if the record was written (new or replaced), False if skipped.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    existing_content = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    record_key = tuple(record.get(f) for f in key_fields)

    if upsert:
        # Keep all lines except any that match the incoming key.
        kept = [
            line
            for line in existing_content.splitlines()
            if line.strip() and tuple(json.loads(line).get(f) for f in key_fields) != record_key
        ]
        kept_content = "\n".join(kept) + ("\n" if kept else "")
        new_content = kept_content + json.dumps(record, separators=(",", ":")) + "\n"
    else:
        for line in existing_content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            existing = json.loads(stripped)
            if tuple(existing.get(f) for f in key_fields) == record_key:
                return False
        if existing_content and not existing_content.endswith("\n"):
            existing_content += "\n"
        new_content = existing_content + json.dumps(record, separators=(",", ":")) + "\n"

    dir_path = file_path.parent
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, file_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    return True


def append_records(
    file_path: Path,
    records: list[dict[str, Any]],
    key_fields: list[str],
    *,
    upsert: bool = False,
) -> int:
    """Write ``records`` to ``file_path``, deduplicating on ``key_fields``.

    When ``upsert=False`` (default): records whose keys already exist in the
    file are skipped.

    When ``upsert=True``: existing records whose keys match any incoming record
    are replaced. All incoming records are always written.

    Reads the file once, processes in memory, then writes atomically via
    temp-file-then-rename.

    Returns:
        The number of records written.
    """
    if not records:
        return 0

    file_path.parent.mkdir(parents=True, exist_ok=True)

    existing_content = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    if existing_content and not existing_content.endswith("\n"):
        existing_content += "\n"

    if upsert:
        # Build the set of incoming keys so we can evict matching existing lines.
        incoming_keys = {tuple(r.get(f) for f in key_fields) for r in records}
        kept_lines = [
            line
            for line in existing_content.splitlines()
            if line.strip() and tuple(json.loads(line).get(f) for f in key_fields) not in incoming_keys
        ]
        kept_content = "\n".join(kept_lines) + ("\n" if kept_lines else "")
        new_lines = [json.dumps(r, separators=(",", ":")) for r in records]
        new_content = kept_content + "\n".join(new_lines) + "\n"
        written = len(new_lines)
    else:
        existing_keys: set[tuple[Any, ...]] = set()
        for line in existing_content.splitlines():
            stripped = line.strip()
            if stripped:
                existing = json.loads(stripped)
                existing_keys.add(tuple(existing.get(f) for f in key_fields))

        new_lines = []
        for record in records:
            key = tuple(record.get(f) for f in key_fields)
            if key not in existing_keys:
                new_lines.append(json.dumps(record, separators=(",", ":")))
                existing_keys.add(key)

        if not new_lines:
            return 0

        new_content = existing_content + "\n".join(new_lines) + "\n"
        written = len(new_lines)

    dir_path = file_path.parent
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, file_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    return written
