"""Nano MVP: print-only, genuine Data Factory -> tokenizer verification.

From repository root:
python -m models.jsm.variants.nano.mvp.scripts.data_pipeline smoke
python -m models.jsm.variants.nano.mvp.scripts.data_pipeline paths
python -m models.jsm.variants.nano.mvp.scripts.data_pipeline preview --manifest ...
"""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from core.paths import STORAGE_DIR
from services.data_factory.src.pipeline import run_local_pipeline
from models.jsm.variants.nano.mvp.src.paths import describe_paths
from models.jsm.variants.nano.mvp.src.tokenization_preview import (
    format_preview,
    preview_candidate_batch,
)


def _smoke() -> dict:
    """Run the real shared Data Factory on synthetic material in temp storage."""
    with tempfile.TemporaryDirectory(prefix="berhot-jsm-nano-bridge-") as temp:
        root = Path(temp)
        input_dir = root / "intake"
        input_dir.mkdir()
        samples = {
            "ar-001": "هذا نص عربي تجريبي للتحقق من سلامة الترميز والاتصال بين المراحل.\n",
            "en-001": "This fictional English sample verifies Data Factory and JSM tokenization.\n",
        }
        specs = []
        for source_id, text in samples.items():
            name = source_id + ".txt"
            data = text.encode("utf-8")
            (input_dir / name).write_bytes(data)
            specs.append({
                "source_id": source_id,
                "relative_path": name,
                "sha256": hashlib.sha256(data).hexdigest(),
                "origin": {
                    "uri": "fixture://jsm-nano/" + source_id,
                    "publisher": "BERHOT synthetic fixture",
                },
                "rights": {
                    "retention_allowed": True,
                    "analysis_allowed": True,
                    "training_allowed": False,
                },
            })
        path = root / "operator-input.json"
        path.write_text(json.dumps({
            "schema_version": "1.0.0",
            "batch_id": "jsm-nano-bridge-smoke-v1",
            "sources": specs,
        }, ensure_ascii=False), encoding="utf-8")
        storage = root / "storage"
        factory = run_local_pipeline(path, input_dir, storage)
        batch = preview_candidate_batch(factory["manifest_path"], storage)
        if batch["verified_sources"] != 2 or not batch["total_preview_tokens"]:
            raise AssertionError("JSM Nano MVP bridge failed")
        return {"factory": factory, "preview": batch}


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="JSM Nano Data Factory/tokenizer print-only connection")
    parser.add_argument("command", choices=("smoke", "preview", "paths"))
    parser.add_argument("--manifest", help="Canonical Data Factory published local-text manifest")
    parser.add_argument("--storage-root", default=str(STORAGE_DIR))
    parser.add_argument("--show-tokens", type=int, default=12)
    args = parser.parse_args(argv)
    if args.command == "paths":
        print(json.dumps(describe_paths(args.storage_root), ensure_ascii=False, indent=2))
    elif args.command == "smoke":
        data = _smoke()
        print("[PASS] Data Factory: selected intake, SHA-256, rights, extraction, cleaning, quality, immutable publication")
        print(format_preview(data["preview"]))
        print("[PASS] Synthetic smoke ran in temporary storage, which is removed after exit.")
    else:
        if not args.manifest:
            parser.error("preview requires --manifest (published by Data Factory)")
        print(format_preview(preview_candidate_batch(
            args.manifest, args.storage_root, show_tokens=args.show_tokens
        )))


if __name__ == "__main__":
    main()
