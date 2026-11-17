# BERHOT AI — modular research and company platform monorepo

**Status: early architecture + runnable local text Data Factory MVP.**
The repo is NOT a production AI serving platform and does not currently
contain trained foundation models or a customer billing system.

## Repository ownership

| Area | Purpose | Current state |
| --- | --- | --- |
| core/ | Shared filesystem paths, settings, immutable local publication | Working small Python foundation |
| services/data_factory/ | Rights-aware, manifest-selected local UTF-8 inspection and processing | Working local text MVP; NOT training-authorized |
| services/memory/, knowledge_graph/, model_dispatcher/ | Shared research services | Scaffolds |
| services/inference/, evaluation/, model_registry/, jobs/, learning/ | Future cross-model capabilities | Documented interfaces only |
| models/ | Independent first-party model families | Most modules are still scaffolds |
| apps/ | Customer and employee UI applications | Planning only |
| platform/ | Identity, tenants, public API, billing, usage, audit | Planning only |
| infrastructure/ | Cloud, compute, databases, security, deployment | Documentation/scaffolds |
| storage/ | Ignored/generated local data, artifacts, releases, logs, state | Layout; R2 plan only |
| docs/ | Architecture, security and operational guidance | Documentation |
| tests/ | Standard library local pipeline and foundation tests | Working tests |

## First working command

Install Python 3.11+ and run from this repository root:

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -e .
    python -m services.data_factory.src.cli smoke-local
    python -m unittest discover -s tests -v

On macOS/Linux, activate using source .venv/bin/activate.

This smoke test uses disposable invented data; no real intake directory,
cloud bucket, model weights, or database is changed.

## Paths

Project-wide local paths are defined in core/paths.py; BERHOT_STORAGE_DIR
can point to a separate local filesystem (recommended outside OneDrive).
Large datasets and checkpoints must not be committed to Git.

Local Data Factory outputs:
  storage/data/processed/text-sha256/
  storage/data/manifests/local-text/

Future approved datasets:
  storage/data/datasets/<family>/<batch-id>/

Family-shared tokenizers:
  storage/artifacts/jsm/tokenizers/<version>/

Model training runs:
  storage/artifacts/<family>/<variant>/<size>/runs/<run-id>/

Approved releases (not yet implemented):
  storage/releases/<family>/

## Important security boundaries

Do NOT treat origin.json, a license string, or a user's manifest claim as
proof of lawful model training. The local Data Factory requires explicitly
declared retention and analysis rights and rejects training_allowed=true.
All its processed results are NOT training-authorized.

The public Git repository currently contains tracked example intake files.
Adding ignore rules does NOT erase previously committed contents or Git
history. Audit their publication and rights; handle removals/history cleanup
as a separate reviewed migration. No historical data was deleted here.

## Guides

- docs/architecture/repository-layout.md
- docs/pipeline-end-to-end.md
- docs/storage.md
- docs/security-and-governance.md
- docs/operations-runbook.md
- services/data_factory/README.md

Model-specific training runs and prior experiments remain unchanged.
