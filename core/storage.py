"""Local immutable publication primitive. Not an R2 client.

A successful write creates a new file once; replay verifies identical bytes.
The temporary file is fully fsynced before atomically linking it into place.
"""
import os
import tempfile
from pathlib import Path


def write_immutable_bytes(destination: str | Path, content: bytes) -> bool:
    if not isinstance(content, bytes):
        raise TypeError("content must be bytes")
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("Refusing to publish through a symlink")
    if path.exists():
        if not path.is_file() or path.read_bytes() != content:
            raise ValueError(f"Immutable storage collision: {path}")
        return False
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=".partial-", delete=False
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp_path, path)
            return True
        except FileExistsError:
            if path.is_symlink() or not path.is_file() or path.read_bytes() != content:
                raise ValueError(f"Immutable storage collision: {path}")
            return False
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
