"""Exact SHA-256 content IDs for deduplication. No semantic dedup yet."""
import hashlib


def content_sha256(content: bytes) -> str:
    if not isinstance(content, bytes):
        raise TypeError("content must be bytes")
    return hashlib.sha256(content).hexdigest()
