"""Explicit local Data Factory CLI. No network or automatic training."""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from core.paths import INTAKE_DIR, STORAGE_DIR
from .pipeline import run_local_pipeline


def smoke_local() -> dict:
    """Exercise actual writes in a disposable temporary directory."""
    with tempfile.TemporaryDirectory(prefix="berhot-data-factory-smoke-") as td:
        root = Path(td)
        intake = root / "intake"
        intake.mkdir()
        sample = b"Original fictional source used only for BERHOT smoke testing.\n"
        digest = hashlib.sha256(sample).hexdigest()
        sources = []
        for i in range(2):
            name = f"sample-{i}.txt"
            (intake / name).write_bytes(sample)
            sources.append({
                "source_id": f"example-{i}",
                "relative_path": name,
                "sha256": digest,
                "origin": {"uri": f"fixture://example/{i}", "publisher": "BERHOT test fixture"},
                "rights": {
                    "retention_allowed": True,
                    "analysis_allowed": True,
                    "training_allowed": False,
                },
            })
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({
            "schema_version": "1.0.0", "batch_id": "smoke-v1", "sources": sources
        }), encoding="utf-8")
        first = run_local_pipeline(manifest, intake, root / "storage")
        replay = run_local_pipeline(manifest, intake, root / "storage")
        if (
            first["processed_objects_created"],
            replay["processed_objects_created"],
            first["exact_duplicates"],
        ) != (1, 0, 1):
            raise AssertionError("Local Data Factory smoke test failed")
        return {
            "result": "passed",
            "created": first["processed_objects_created"],
            "replay_created": replay["processed_objects_created"],
            "exact_duplicates": first["exact_duplicates"],
            "training_allowed": False,
            "temporary_data_removed_on_exit": True,
        }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="BERHOT local Data Factory")
    parser.add_argument("command", choices=("smoke-local", "run-local"))
    parser.add_argument("--manifest")
    parser.add_argument("--intake-root", default=str(INTAKE_DIR))
    parser.add_argument("--storage-root", default=str(STORAGE_DIR))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "smoke-local":
        result = smoke_local()
    else:
        if not args.manifest:
            parser.error("run-local requires --manifest")
        result = run_local_pipeline(
            args.manifest, args.intake_root, args.storage_root,
            dry_run=args.dry_run,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
