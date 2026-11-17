"""Inspect explicitly selected text files before publication.

Reject path escapes, symlinks, binary garbage, unexpected extensions,
invalid UTF-8, oversized bytes and hash mismatches. Not a malware scanner.
"""
import hashlib
import re
from pathlib import Path, PurePosixPath

_SHA = re.compile(r"^[0-9a-f]{64}$")
MAX_FILE_BYTES = 2_000_000


def inspect_text_file(intake_root: str | Path, relative_path: str,
                      expected_sha256: str) -> tuple[bytes, str]:
    if (not isinstance(relative_path, str) or not relative_path
        or "\\" in relative_path or ":" in relative_path
        or "\x00" in relative_path):
        raise ValueError("Expected safe POSIX relative path")
    rel = PurePosixPath(relative_path)
    if (rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() != ".txt"
        or rel.name.startswith(".")):
        raise ValueError("Only in-root .txt input files are allowed")
    if not isinstance(expected_sha256, str) or not _SHA.fullmatch(expected_sha256):
        raise ValueError("Expected lowercase SHA-256 hex")
    root = Path(intake_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Invalid intake root")
    selected = root
    for component in rel.parts:
        selected = selected / component
        if selected.is_symlink():
            raise ValueError("Symlink inputs are prohibited")
    path = selected.resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError("Input escapes intake root")
    if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Input is not a supported text file or exceeds 2 MB")
    content = path.read_bytes()
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Input exceeds 2 MB")
    if hashlib.sha256(content).hexdigest() != expected_sha256:
        raise ValueError("Input SHA-256 mismatch")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Input is not UTF-8") from exc
    if not text.strip() or "\x00" in text:
        raise ValueError("Empty text or NUL byte detected")
    return content, text
