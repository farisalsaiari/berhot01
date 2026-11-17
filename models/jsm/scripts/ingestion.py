"""Legacy JSM entry point forwarded to shared Data Factory.

Use from BERHOT repository root:
python -m models.jsm.scripts.ingestion smoke-local
"""
from services.data_factory.src.cli import main

if __name__ == "__main__":
    main()
