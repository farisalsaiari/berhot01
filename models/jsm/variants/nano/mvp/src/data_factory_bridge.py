"""Verified, read-only bridge from Data Factory local-text manifests to JSM.

Never infer training authorization from source content or a directory name.
Only accepts the canonical local-text-v1 manifest produced by the factory,
with every processed SHA-256 object revalidated before any tokenization.
"""
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

_MAX_MANIFEST_BYTES = 1_000_000
_MAX_TEXT_BYTES = 2_000_000
_SHA = re.compile(r"^[0-9a-f]{64}$")
_BATCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


@dataclass(frozen=True)
class CandidateText:
    source_id: str
    sha256: str
    text: str


@dataclass(frozen=True)
class VerifiedCandidateBatch:
    batch_id: str
    manifest_sha256: str
    records: tuple[CandidateText, ...]
    unique_processed_objects: int
    training_allowed: bool = False


def _check_file(path: Path, root: Path, max_bytes: int) -> bytes:
    if path.is_symlink() or not path.is_file() or not path.resolve(strict=True).is_relative_to(root):
        raise ValueError("Unsupported, symlinked, or out-of-root artifact")
    if path.stat().st_size > max_bytes:
        raise ValueError("Artifact exceeds allowed size")
    data = path.read_bytes()
    if len(data) > max_bytes:
        raise ValueError("Artifact exceeds allowed size")
    return data


def load_verified_candidate(manifest_path: str | Path, storage_root: str | Path) -> VerifiedCandidateBatch:
    """Verify ALL objects and declared rights; read-only, no output files."""
    storage = Path(storage_root).expanduser().resolve(strict=True)
    manifests = storage / "data" / "manifests" / "local-text"
    objects = storage / "data" / "processed" / "text-sha256"
    manifest_path = Path(manifest_path).expanduser()
    if not manifest_path.is_absolute():
        manifest_path = manifest_path.resolve(strict=True)
    raw_manifest = _check_file(manifest_path, manifests.resolve(strict=True), _MAX_MANIFEST_BYTES)
    try:
        manifest = json.loads(raw_manifest.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid Data Factory manifest") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0.0":
        raise ValueError("Unsupported Data Factory manifest schema")
    batch_id = manifest.get("batch_id")
    if not isinstance(batch_id, str) or not _BATCH.fullmatch(batch_id):
        raise ValueError("Unsafe batch ID")
    if manifest_path.name != batch_id + ".json":
        raise ValueError("Data Factory manifest path/name mismatch")
    if manifest.get("data_factory_processor") != "local-text-v1":
        raise ValueError("Expected local text Data Factory processor")
    if manifest.get("status") != "processed_candidate_not_training_authorized":
        raise ValueError("Unexpected Data Factory status")
    if manifest.get("training_allowed") is not False:
        raise PermissionError("Candidate manifest may never authorize training")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 50:
        raise ValueError("Invalid batch sources")
    records = []
    seen_sources = set()
    unique_hashes = set()
    for item in sources:
        if not isinstance(item, dict):
            raise ValueError("Invalid candidate record")
        source_id = item.get("source_id")
        if not isinstance(source_id, str) or not _BATCH.fullmatch(source_id) or source_id in seen_sources:
            raise ValueError("Missing, unsafe or duplicate source ID")
        seen_sources.add(source_id)
        rights = item.get("rights")
        if not isinstance(rights, dict) or rights.get("training_allowed") is not False:
            raise PermissionError("Candidate source cannot be used for model training")
        if rights.get("analysis_allowed") is not True or rights.get("retention_allowed") is not True:
            raise PermissionError("Candidate source lacks analysis/retention declaration")
        origin = item.get("origin")
        if not isinstance(origin, dict) or origin.get("verification") != "operator_declared_not_independently_verified":
            raise ValueError("Missing declared provenance marker")
        quality = item.get("quality")
        if not isinstance(quality, dict) or quality.get("passed") is not True:
            raise ValueError("Only Data Factory quality-passed candidates can be previewed")
        digest = item.get("processed_sha256")
        original_digest = item.get("source_sha256")
        if not isinstance(digest, str) or not _SHA.fullmatch(digest):
            raise ValueError("Invalid processed object SHA-256")
        if not isinstance(original_digest, str) or not _SHA.fullmatch(original_digest):
            raise ValueError("Invalid original source SHA-256")
        if item.get("processed_relative_path") != "text-sha256/" + digest + ".txt":
            raise ValueError("Mismatched or unsafe processed relative path")
        object_path = objects / (digest + ".txt")
        content = _check_file(object_path, objects.resolve(strict=True), _MAX_TEXT_BYTES)
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("Processed object SHA-256 mismatch")
        try:
            text = content.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ValueError("Processed content not UTF-8") from exc
        if not text.strip() or "\x00" in text:
            raise ValueError("Invalid processed text")
        records.append(CandidateText(source_id, digest, text))
        unique_hashes.add(digest)
    if manifest.get("unique_processed_objects") != len(unique_hashes):
        raise ValueError("Data Factory unique object count mismatch")
    return VerifiedCandidateBatch(
        batch_id=batch_id,
        manifest_sha256=hashlib.sha256(raw_manifest).hexdigest(),
        records=tuple(records),
        unique_processed_objects=len(unique_hashes),
    )
