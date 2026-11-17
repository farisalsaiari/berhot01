# BERHOT storage layout and Cloudflare R2 guidance

Local root defaults to repo/storage, overridable with BERHOT_STORAGE_DIR.

Local canonical locations:
  storage/data/incoming/
  storage/data/raw/
  storage/data/processed/
  storage/data/manifests/
  storage/data/datasets/<family>/<batch-id>/    (future approved releases)
  storage/artifacts/jsm/tokenizers/<version>/
  storage/artifacts/<family>/<variant>/<size>/runs/<run-id>/
  storage/releases/<family>/                   (future approved checkpoints)
  storage/logs/<service>/
  storage/state/
  storage/cache/
  storage/tmp/

Store dataset content once and reference it in each training run manifest
through immutable IDs and SHA-256, not by copying entire corpora into runs.
Checkpoints and metrics stay under their originating run. A release manifest
refers to a reviewed checkpoint and should not overwrite the old one.

The present R2 proposal maps storage/data, storage/memory and
storage/artifacts to three PRIVATE buckets. There is NO automatic R2
implementation or provisioning in this repository. A production adapter must
handle credentials separately, object immutability, lifecycle, private ACLs,
checksums and reversible disaster recovery.

Do not sync storage/state, storage/cache, storage/tmp or raw local intake to
R2 as part of a blanket folder upload. Live SQLite database snapshots require
a database-aware backup protocol, not copying an active file blindly.

For Windows/OneDrive, configure a local data root outside OneDrive:

    $env:BERHOT_STORAGE_DIR = "D:\BERHOT\storage"

Set it before starting Python. Treat this as local scratch/working storage
unless backed by an independently tested durable storage system.
