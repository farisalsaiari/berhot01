"""Validate an explicit local intake manifest. Never scan whole directories."""
import json
import re
from pathlib import Path

_BATCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
MAX_SOURCES = 50
MAX_MANIFEST_BYTES = 1_000_000


def load_manifest(path: str | Path) -> dict:
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("Manifest missing or too large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Manifest must be valid UTF-8 JSON") from error
    if not isinstance(data, dict) or data.get("schema_version") != "1.0.0":
        raise ValueError("Expected schema_version 1.0.0")
    batch_id = data.get("batch_id")
    if not isinstance(batch_id, str) or not _BATCH.fullmatch(batch_id) or batch_id in (".", ".."):
        raise ValueError("Invalid batch_id")
    sources = data.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= MAX_SOURCES:
        raise ValueError("sources must contain between 1 and 50 items")
    seen = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Each source must be an object")
        sid = source.get("source_id")
        if not isinstance(sid, str) or not _BATCH.fullmatch(sid):
            raise ValueError("Invalid source_id")
        if sid in seen:
            raise ValueError("Duplicate source_id")
        seen.add(sid)
        for key in ("relative_path", "sha256"):
            if not isinstance(source.get(key), str):
                raise ValueError(f"Missing {key} for {sid}")
        if not isinstance(source.get("origin"), dict):
            raise ValueError(f"Missing provenance for {sid}")
        if not isinstance(source.get("rights"), dict):
            raise ValueError(f"Missing rights for {sid}")
    return data
