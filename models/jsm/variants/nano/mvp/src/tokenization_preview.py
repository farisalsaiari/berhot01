"""Preview only: verify Data Factory handoff, tokenize, print status.

Intentionally DOES NOT publish data/datasets/jsm, write train-ready shards,
train a tokenizer, update model weights, or run an optimizer.
"""
import hashlib
import json
from pathlib import Path

from models.jsm.src.tokenization.tokenizer import JSMByteTokenizer
from .data_factory_bridge import load_verified_candidate
from .paths import describe_paths


def preview_candidate_batch(manifest_path, storage_root, *, show_tokens: int = 12) -> dict:
    if not isinstance(show_tokens, int) or isinstance(show_tokens, bool) or not 0 <= show_tokens <= 100:
        raise ValueError("show_tokens must be between 0 and 100")
    batch = load_verified_candidate(manifest_path, storage_root)
    tokenizer = JSMByteTokenizer()
    details = []
    total_tokens = 0
    unique_hashes = set()
    for record in batch.records:
        ids = tokenizer.encode(record.text)
        if tokenizer.decode(ids) != record.text:
            raise ValueError("Tokenizer round-trip failure")
        total_tokens += len(ids)
        unique_hashes.add(record.sha256)
        details.append({
            "source_id": record.source_id,
            "processed_sha256": record.sha256,
            "token_count": len(ids),
            "token_preview": ids[:show_tokens],
            "round_trip_ok": True,
        })
    # Text content is never printed in plain form by this preview. No writes.
    return {
        "status": "CANDIDATE_PREVIEW_ONLY",
        "batch_id": batch.batch_id,
        "data_factory_manifest_sha256": batch.manifest_sha256,
        "verified_sources": len(batch.records),
        "unique_processed_objects": len(unique_hashes),
        "tokenizer": tokenizer.tokenizer_id,
        "tokenizer_kind": "reversible_utf8_bytes_not_trained_bpe",
        "total_preview_tokens": total_tokens,
        "records": details,
        "planned_train_ready_location": str(
            Path(storage_root).expanduser().resolve() / "data" / "datasets" / "jsm" / batch.batch_id
        ),
        "train_ready_export": "BLOCKED_NO_INDEPENDENT_RIGHTS_APPROVAL",
        "model_training_started": False,
        "files_written_by_jsm": 0,
    }


def format_preview(result: dict) -> str:
    lines = [
        "[JSM Nano MVP] Data Factory -> JSM -> tokenizer connection",
        f"[PASS] Data Factory candidate batch: {result['batch_id']}",
        f"[PASS] Manifest SHA-256: {result['data_factory_manifest_sha256']}",
        f"[PASS] Verified source records: {result['verified_sources']}",
        f"[PASS] Unique processed objects: {result['unique_processed_objects']}",
        f"[PASS] JSM tokenizer: {result['tokenizer']}",
        f"[PASS] Preview token count: {result['total_preview_tokens']}",
    ]
    for row in result["records"]:
        lines.append(
            f"[PASS] {row['source_id']}: {row['token_count']} tokens, "
            f"first IDs={row['token_preview']}, decode_ok={row['round_trip_ok']}"
        )
    lines += [
        f"[PLAN] Future approved dataset target: {result['planned_train_ready_location']}",
        "[BLOCKED] Training-ready publication requires independently verified training eligibility.",
        "[SKIP] No JSM dataset shard, model weights, checkpoint or training job created.",
    ]
    return "\n".join(lines)
