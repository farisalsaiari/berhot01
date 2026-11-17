"""No duplicate filesystem roots: derive Nano MVP paths from BERHOT/JSM."""
from pathlib import Path
from core.paths import STORAGE_DIR, PROCESSED_DIR, MANIFESTS_DIR
from models.jsm.src.core.paths import JSM_DATASETS_DIR, JSM_TOKENIZERS_DIR, get_run_dir

MVP_ROOT = Path(__file__).resolve().parents[1]
MVP_EXAMPLE_RUN_DIR = get_run_dir("nano", "mvp", "preview-only")


def describe_paths(storage_root=None) -> dict:
    """Read-only path diagnostics. Do not create directories."""
    root = STORAGE_DIR if storage_root is None else Path(storage_root).expanduser().resolve()
    return {
        "mvp_source_dir": str(MVP_ROOT),
        "storage_root": str(root),
        "processed_text_dir": str(root / "data" / "processed" / "text-sha256"),
        "data_factory_manifests_dir": str(root / "data" / "manifests" / "local-text"),
        "jsm_training_datasets_dir": str(root / "data" / "datasets" / "jsm"),
        "jsm_family_tokenizer_artifacts_dir": str(root / "artifacts" / "jsm" / "tokenizers"),
        "nano_mvp_runs_dir": str(root / "artifacts" / "jsm" / "nano" / "mvp" / "runs"),
    }
