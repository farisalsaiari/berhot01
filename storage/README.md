# Local storage workspace

This directory is the local counterpart of company object storage.
See the [storage guide](../docs/storage.md) for naming, lifecycle, examples,
and terminal commands for R2.

| Local directory | Proposed destination | Purpose |
| --- | --- | --- |
| `data/` | `s3://berhot-data/` | Raw, processed, curated datasets, catalogs, manifests, splits, templates |
| `memory/` | `s3://berhot-memory/` | Shared evidence, model views and memory snapshots |
| `artifacts/` | `s3://berhot-artifacts/` | Checkpoints and outputs for every family |
| `incoming/` | Local only | Incomplete downloads and unreviewed imports |
| `cache/` | Local only | Re-downloadable datasets and models |
| `tmp/` | Local only | Disposable processing scratch space |

Payload files in these directories are ignored by Git. Only `.gitkeep` files
preserve the directory scaffold. Put documentation and configuration intended for
Git in `docs/`, `configs/`, `tests/fixtures/`, or model directories instead.
All generated catalogs, manifests, splits and dataset templates belong under
`storage/data/` (ignored by Git except for `.gitkeep` markers).
The existing MVP assets remain in their original MVP locations until migration.

The three R2 bucket names are proposals. No buckets, credentials, or uploads have been
configured. `r2.example.json` records the planned mapping; it is documentation,
not automatically loaded by training code or sync commands.

Only `storage/data/`, `storage/memory/` and `storage/artifacts/` are future upload roots. Do not sync the
whole repository or `storage/` root.

## Autonomous-learning architecture extension (proposed)

- `data/datasets/<family>/<release>/`: frozen training-ready releases, **not the existing current data factory extraction output**. Payloads remain ignored by Git.
- `memory/capabilities/`, `memory/curiosity/`, `memory/learning-history/`: future exported model capability records, research questions and audit receipts. The authoritative live database would be a trusted service.
- `state/`: proposed durable LOCAL databases and backups. No active SQLite DB was moved; this folder must never be included in future generic R2 sync.
- `artifacts/sora/`: placeholder for a provisional image/design family; brand/name still subject to review.

**Critical:** Until a tested DB migration occurs, the real SQLite prototype lives under `storage/tmp/memory/berhot.sqlite3`. Do NOT assume this DB is disposable merely because of its path. See [runbook](../docs/operations-runbook.md) and [Pipeline](../docs/pipeline-end-to-end.md).
