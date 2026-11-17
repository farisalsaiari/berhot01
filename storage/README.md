# BERHOT local storage workspace

The global root is defined by core/paths.py and may be placed outside OneDrive
with BERHOT_STORAGE_DIR. Git ignores generated corpora, checkpoints, logs,
state, quarantine and released model files.

- data/incoming: untrusted intake batches.
- data/raw: future source-preserving object store.
- data/processed: candidate Data Factory output (NOT training authorized).
- data/manifests: source/provenance and processing manifests.
- data/datasets/<family>/<batch-id>: future frozen APPROVED training releases.
- artifacts/jsm/tokenizers/<version>: family-shared tokenizer versions.
- artifacts/<family>/<variant>/<size>/runs/<run-id>: weights and run metrics.
- releases/<family>: future reviewed model deployments.
- memory: future sourced memory export data.
- state: durable databases, requiring database-aware backup.
- logs: service operational logs.
- cache, tmp: local transient files.
- quarantine: suspicious/rejected sources requiring review.

Private Cloudflare R2 bucket mappings in r2.example.json are only a plan.
Never sync the whole repository or a live SQLite database indiscriminately.
If any previous prototype database lives in storage/tmp, DO NOT delete it
without verifying and migrating its backups first.

See ../docs/storage.md.
