"""Authoritative local filesystem roots for the BERHOT monorepo.

No directories are created at import time. Cloud object keys are *not* Paths.
Set BERHOT_STORAGE_DIR to keep large artifacts outside OneDrive.
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIGS_DIR = PROJECT_ROOT / "core" / "configs"
INTAKE_DIR = PROJECT_ROOT / "intake"
MODELS_DIR = PROJECT_ROOT / "models"
SERVICES_DIR = PROJECT_ROOT / "services"
INFRASTRUCTURE_DIR = PROJECT_ROOT / "infrastructure"

STORAGE_DIR = Path(
    os.environ.get("BERHOT_STORAGE_DIR") or str(PROJECT_ROOT / "storage")
).expanduser().resolve()
DATA_DIR = STORAGE_DIR / "data"
INCOMING_DIR = DATA_DIR / "incoming"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DATASETS_DIR = DATA_DIR / "datasets"
MANIFESTS_DIR = DATA_DIR / "manifests"
ARTIFACTS_DIR = STORAGE_DIR / "artifacts"
RELEASES_DIR = STORAGE_DIR / "releases"
LOGS_DIR = STORAGE_DIR / "logs"
STATE_DIR = STORAGE_DIR / "state"
CACHE_DIR = STORAGE_DIR / "cache"
TMP_DIR = STORAGE_DIR / "tmp"
QUARANTINE_DIR = STORAGE_DIR / "quarantine"
