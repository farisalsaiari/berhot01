"""JSM-only paths derived from shared BERHOT local filesystem roots."""
import re
from core.paths import DATASETS_DIR, ARTIFACTS_DIR, RELEASES_DIR

JSM_DATASETS_DIR = DATASETS_DIR / "jsm"
JSM_ARTIFACTS_DIR = ARTIFACTS_DIR / "jsm"
JSM_TOKENIZERS_DIR = JSM_ARTIFACTS_DIR / "tokenizers"
JSM_RELEASES_DIR = RELEASES_DIR / "jsm"
_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")


def _safe(part: str) -> str:
    if not isinstance(part, str) or not _SEGMENT.fullmatch(part):
        raise ValueError("Unsafe JSM run path segment")
    return part


def get_run_dir(variant: str, size: str, run_id: str):
    return JSM_ARTIFACTS_DIR / _safe(variant) / _safe(size) / "runs" / _safe(run_id)
