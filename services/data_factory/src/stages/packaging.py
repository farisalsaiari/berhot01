"""Deterministic bytes for versioned, immutable manifest publication."""
import json


def manifest_bytes(manifest: dict) -> bytes:
    if not isinstance(manifest, dict):
        raise TypeError("manifest must be dict")
    return (json.dumps(
        manifest, ensure_ascii=False, indent=2, sort_keys=True,
        separators=(",", ": ")
    ) + "\n").encode("utf-8")
