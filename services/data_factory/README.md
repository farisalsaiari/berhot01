# BERHOT Data Factory — local text MVP

**Status:** This service can run a safe, explicit, operator-driven local
UTF-8 text preparation pipeline. It is NOT a train-ready dataset exporter.

Working stages are ingestion, inspection, extraction, cleaning, normalization,
exact deduplication, simple quality checks, declared provenance, fail-closed
rights checks and deterministic immutable publication. Modules live in src/stages.

## CLI, run from repository root

    python -m services.data_factory.src.cli smoke-local
    python -m services.data_factory.src.cli run-local --manifest batch.json --intake-root intake --dry-run
    python -m services.data_factory.src.cli run-local --manifest batch.json --intake-root intake

Example JSON manifest:

    {
      "schema_version": "1.0.0",
      "batch_id": "operator-batch-0001",
      "sources": [{
        "source_id": "example-01",
        "relative_path": "sample.txt",
        "sha256": "<replace with actual 64-character lowercase SHA-256>",
        "origin": {"uri": "fixture://example", "publisher": "Example publisher"},
        "rights": {
          "retention_allowed": true,
          "analysis_allowed": true,
          "training_allowed": false
        }
      }]
    }

Maximum: 50 explicitly selected .txt files, <=2 MB per file, <=20 MB
combined. No directory crawling, unsafe relative paths, symlink inputs,
binary text, or train permissions. An input with one failed source rejects
the whole batch before publication.

Outputs:
  storage/data/processed/text-sha256/<processed_hash>.txt
  storage/data/manifests/local-text/<batch_id>.json

Replaying an unchanged batch has no duplicate effect. Source originals are
never rewritten. The manifests record source and derived content hashes and
operator-declared (NOT independently verified) provenance and permissions.

Not implemented: authenticated rights approval, PDF/DOCX extraction, image,
audio/video/3D processing, semantic dedup, PII or malware scanning, model
training, frozen train/validation/test releases, cloud object-store writes.
A separate authorized dataset release is required before GPU training.
