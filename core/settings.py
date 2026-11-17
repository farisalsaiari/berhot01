"""Small validated environment settings; not a secrets or R2 client."""
from dataclasses import dataclass
import os
from pathlib import Path

from .paths import STORAGE_DIR

VALID_ENVIRONMENTS = frozenset({"development", "test", "production"})

@dataclass(frozen=True)
class Settings:
    environment: str
    storage_dir: Path

def load_settings() -> Settings:
    environment = os.getenv("BERHOT_ENV", "development").strip().lower()
    if environment not in VALID_ENVIRONMENTS:
        raise ValueError("BERHOT_ENV must be development, test, or production")
    storage = Path(os.getenv("BERHOT_STORAGE_DIR") or str(STORAGE_DIR))
    return Settings(environment=environment, storage_dir=storage.expanduser().resolve())
