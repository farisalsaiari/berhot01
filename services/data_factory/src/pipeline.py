"""Explicit, idempotent local UTF-8 text preparation.

Preflights a whole batch before publication. Outputs are only
content-addressed processed text and an immutable provenance manifest.
Never authorizes training or opens sealed evaluation corpora.
"""
from pathlib import Path

from core.storage import write_immutable_bytes
from .stages.ingestion import load_manifest
from .stages.inspection import inspect_text_file
from .stages.extraction import extract_text
from .stages.cleaning import clean_text
from .stages.normalization import normalize_text
from .stages.deduplication import content_sha256
from .stages.quality import check_text_quality
from .stages.provenance import declared_origin
from .stages.rights_eligibility import inspect_declared_rights
from .stages.packaging import manifest_bytes

MAX_BATCH_BYTES = 20_000_000


def run_local_pipeline(
    manifest_path: str | Path,
    intake_root: str | Path,
    storage_root: str | Path,
    *,
    dry_run: bool = False,
) -> dict:
    """Process only manifest-listed files. Immutable writes can be replayed."""
    spec = load_manifest(manifest_path)
    root = Path(storage_root).expanduser().resolve()
    processed_root = root / "data" / "processed" / "text-sha256"
    manifest_file = root / "data" / "manifests" / "local-text" / (spec["batch_id"] + ".json")
    records: list[dict] = []
    objects: dict[str, bytes] = {}
    total = 0
    for source in spec["sources"]:
        rights = inspect_declared_rights(source["rights"])
        origin = declared_origin(source)
        raw, decoded = inspect_text_file(
            intake_root, source["relative_path"], source["sha256"]
        )
        total += len(raw)
        if total > MAX_BATCH_BYTES:
            raise ValueError("Local text batch exceeds 20 MB")
        text = normalize_text(clean_text(extract_text(decoded)))
        quality = check_text_quality(text)
        if not quality["passed"]:
            raise ValueError(
                f"Rejected source {source['source_id']}: {quality['reasons']}"
            )
        processed = text.encode("utf-8")
        digest = content_sha256(processed)
        objects[digest] = processed
        records.append({
            "source_id": source["source_id"],
            "relative_path": source["relative_path"],
            "source_sha256": content_sha256(raw),
            "processed_sha256": digest,
            "processed_relative_path": "text-sha256/" + digest + ".txt",
            "origin": origin,
            "rights": rights,
            "quality": quality,
        })
    published = {
        "schema_version": "1.0.0",
        "batch_id": spec["batch_id"],
        "status": "processed_candidate_not_training_authorized",
        "training_allowed": False,
        "data_factory_processor": "local-text-v1",
        "sources": records,
        "unique_processed_objects": len(objects),
    }
    canonical = manifest_bytes(published)
    # Preflight ALL existing objects and immutable batch ID before any writes.
    if manifest_file.exists() or manifest_file.is_symlink():
        if (manifest_file.is_symlink() or not manifest_file.is_file()
            or manifest_file.read_bytes() != canonical):
            raise ValueError("Immutable batch ID already has different contents")
    for digest, payload in objects.items():
        obj = processed_root / (digest + ".txt")
        if obj.exists() or obj.is_symlink():
            if obj.is_symlink() or not obj.is_file() or obj.read_bytes() != payload:
                raise ValueError("Existing processed object corrupted")
    created = 0
    if not dry_run:
        for digest, payload in objects.items():
            created += int(write_immutable_bytes(
                processed_root / (digest + ".txt"), payload
            ))
        write_immutable_bytes(manifest_file, canonical)
    return {
        "batch_id": spec["batch_id"],
        "sources": len(records),
        "unique_processed_objects": len(objects),
        "exact_duplicates": len(records) - len(objects),
        "processed_objects_created": created,
        "manifest_path": str(manifest_file),
        "training_allowed": False,
        "model_training_started": False,
        "independently_verified_rights": False,
        "dry_run": dry_run,
    }
