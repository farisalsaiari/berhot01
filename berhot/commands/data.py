"""Company Data Factory CLI facade; only the existing text MVP executes."""
import json
from pathlib import Path

from core.paths import INTAKE_DIR, STORAGE_DIR
from services.data_factory.src.cli import smoke_local
from services.data_factory.src.pipeline import run_local_pipeline
from .common import show, unavailable


def configure(parent) -> None:
    actions = parent.add_subparsers(dest="data_action", required=True)

    for name, help_text in (
        ("inspect", "Validate a selected source manifest; no files written"),
        ("process", "Publish immutable processed candidate text and manifest"),
    ):
        cmd = actions.add_parser(name, help=help_text)
        cmd.add_argument("--manifest", required=True, help="Explicit input JSON manifest")
        cmd.add_argument("--intake-root", default=str(INTAKE_DIR))
        cmd.add_argument("--storage-root", default=str(STORAGE_DIR))
        if name == "process":
            cmd.add_argument("--dry-run", action="store_true")
        cmd.set_defaults(handler=_run)

    smoke = actions.add_parser("smoke", help="Run an isolated synthetic Data Factory smoke test")
    smoke.set_defaults(handler=_smoke)

    elig = actions.add_parser(
        "eligibility", help="Check why a local candidate is not train-authorized"
    )
    elig.add_argument("--manifest", required=True, help="Published local-text manifest")
    elig.add_argument("--storage-root", default=str(STORAGE_DIR))
    elig.add_argument("--family", default="jsm")
    elig.set_defaults(handler=_eligibility)

    publish = actions.add_parser(
        "publish", help="RESERVED: approved train-ready dataset release (blocked)"
    )
    publish.add_argument("--batch", required=True)
    publish.add_argument("--family", required=True)
    publish.set_defaults(handler=_publish)


def _run(args) -> int:
    dry_run = args.data_action == "inspect" or bool(getattr(args, "dry_run", False))
    report = run_local_pipeline(
        args.manifest, args.intake_root, args.storage_root, dry_run=dry_run
    )
    show({"operation": "data." + args.data_action,
          "status": "VALIDATED_NO_WRITES" if dry_run else "PROCESSED_CANDIDATE_ONLY",
          **report})
    return 0


def _smoke(args) -> int:
    show({"operation": "data.smoke", **smoke_local()})
    return 0


def _eligibility(args) -> int:
    # This is a candidate-status query, NOT rights authentication.
    root = Path(args.storage_root).expanduser().resolve(strict=True)
    manifests = (root / "data" / "manifests" / "local-text").resolve(strict=True)
    path = Path(args.manifest).expanduser().resolve(strict=True)
    if not path.is_relative_to(manifests) or path.suffix.lower() != ".json":
        raise ValueError("Expected a published Data Factory local-text manifest")
    if path.stat().st_size > 1_000_000:
        raise ValueError("Manifest too large")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("data_factory_processor") != "local-text-v1":
        raise ValueError("Unsupported Data Factory manifest")
    if manifest.get("status") != "processed_candidate_not_training_authorized" or manifest.get("training_allowed") is not False:
        raise ValueError("Unexpected candidate status; cannot approve training")
    show({
        "operation": "data.eligibility",
        "status": "BLOCKED_NOT_TRAIN_READY",
        "family": args.family,
        "batch_id": manifest.get("batch_id"),
        "training_allowed": False,
        "independently_verified_rights": False,
        "message": "Local-text intake has only operator-declared analysis rights. Dataset approval is not implemented.",
    })
    return 0


def _publish(args) -> int:
    return unavailable(
        "data.publish",
        "An independent, authenticated training-rights review and frozen train/validation/test dataset exporter do not exist. Candidate text cannot be published as train-ready."
    )
