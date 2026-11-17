"""One-command orchestration of the *currently* working local text + Nano preview."""
from core.paths import INTAKE_DIR, STORAGE_DIR
from services.data_factory.src.pipeline import run_local_pipeline
from models.jsm.variants.nano.mvp.src.tokenization_preview import (
    preview_candidate_batch, format_preview,
)
from models.jsm.variants.nano.mvp.scripts.data_pipeline import _smoke
from .common import show, unavailable


def configure(parent) -> None:
    actions = parent.add_subparsers(dest="pipeline_action", required=True)
    smoke = actions.add_parser("smoke", help="Synthetic Arabic/English full bridge smoke")
    smoke.set_defaults(handler=_smoke_handler)

    run = actions.add_parser("run", help="Process local-text batch and preview Nano tokens")
    run.add_argument("--manifest", required=True, help="Explicit source manifest")
    run.add_argument("--intake-root", default=str(INTAKE_DIR))
    run.add_argument("--storage-root", default=str(STORAGE_DIR))
    run.add_argument("--family", default="jsm")
    run.add_argument("--variant", default="nano")
    run.add_argument("--size", default="mvp")
    run.add_argument("--show-tokens", type=int, default=12)
    run.set_defaults(handler=_run)


def _smoke_handler(args) -> int:
    data = _smoke()
    show({
        "operation": "pipeline.smoke",
        "status": "PASSED_CANDIDATE_PREVIEW",
        "factory_sources": data["factory"]["sources"],
        "verified_records": data["preview"]["verified_sources"],
        "tokenizer_id": data["preview"]["tokenizer"],
        "total_preview_tokens": data["preview"]["total_preview_tokens"],
        "training_ready_export": False,
        "gpu_training_started": False,
    })
    return 0


def _run(args) -> int:
    if (args.family, args.variant, args.size) != ("jsm", "nano", "mvp"):
        return unavailable(
            "pipeline.run",
            "Only the real local text -> jsm/nano/mvp preview bridge is wired. Other families/variants need dedicated adapters."
        )
    # Process then PREVIEW the exact immutable Data Factory output. No train.
    result = run_local_pipeline(args.manifest, args.intake_root, args.storage_root)
    preview = preview_candidate_batch(
        result["manifest_path"], args.storage_root, show_tokens=args.show_tokens
    )
    print("[PASS] Shared Data Factory published processed CANDIDATE text.")
    print(format_preview(preview))
    print("[PASS] Connected pipeline completed without training or dataset release.")
    return 0
