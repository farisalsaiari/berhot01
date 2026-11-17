# BERHOT local operator runbook

The project is early-stage; no production deployment or GPU fleet is managed.

From Windows PowerShell in the project root (Python >=3.11):

    py -3.11 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -e .
    python -m unittest discover -s tests -v
    python -m services.data_factory.src.cli smoke-local

For macOS/Linux, create/activate a venv using python3 and
source .venv/bin/activate, then run the same Python module commands.

For a real text source, make your own explicit JSON manifest with accurate
SHA-256 and documented retention/analysis permissions. Begin with
--dry-run, then execute run-local, never targeting a broad directory scan.

When a batch fails, do not edit its published manifest. Use a new batch
ID if the source content changed; review partial unreferenced objects
before garbage collection. Never delete old model checkpoints or frozen
holdout reports to make a new experiment succeed.

No production release procedure is implemented. Infrastructure README files
describe plans, not running deployments.
