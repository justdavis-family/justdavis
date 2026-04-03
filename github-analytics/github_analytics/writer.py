"""NDJSON writer with idempotent append and atomic file writes."""

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
) -> bool:
    """Append ``record`` to ``file_path`` if no existing record matches on ``key_fields``.

    Creates the file (and parent directories) if they don't exist.
    Uses atomic temp-file-then-rename to avoid partial writes.

    Returns:
        True if the record was appended, False if it was already present.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    record_key = tuple(record[f] for f in key_fields)

    # Check for existing record with the same key
    if file_path.exists():
        for line in file_path.read_text().splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            existing = json.loads(stripped)
            if tuple(existing.get(f) for f in key_fields) == record_key:
                return False

    # Atomic append: read existing content, append new line, write via rename
    existing_content = file_path.read_text() if file_path.exists() else ""
    new_content = existing_content + json.dumps(record, separators=(",", ":")) + "\n"

    dir_path = file_path.parent
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(new_content)
        os.replace(tmp_path, file_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    return True
