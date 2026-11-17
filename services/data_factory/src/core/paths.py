"""Data Factory-only locations: import shared roots; do not redefine them."""
from core.paths import DATA_DIR, MANIFESTS_DIR, PROCESSED_DIR, QUARANTINE_DIR

TEXT_OBJECTS_DIR = PROCESSED_DIR / "text-sha256"
LOCAL_BATCH_MANIFESTS_DIR = MANIFESTS_DIR / "local-text"
LOCAL_QUARANTINE_DIR = QUARANTINE_DIR / "data_factory"
