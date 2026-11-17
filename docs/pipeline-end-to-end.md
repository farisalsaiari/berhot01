# BERHOT end-to-end data and model pipeline

## Current execution (implemented)

1. Operator selects explicit local UTF-8 files in a JSON manifest.
2. Require declared retention + analysis permissions; explicitly reject training permission.
3. Inspect safe relative .txt path, source hash, file size and valid UTF-8.
4. Conservative whitespace cleanup and Unicode NFC normalization.
5. Simple quality gates and exact SHA-256 deduplication.
6. Publish immutable content-addressed processed text plus a source manifest.
7. No model training, memory writes, hidden holdout consumption or network access.

Command: python -m services.data_factory.src.cli smoke-local

The pipeline is local and operator-attested; it does NOT independently verify
legal rights. A text passing inspection is not automatically fit for training.

## Intended future architecture (NOT implemented)

Collection -> Inspection -> Source/rights adjudication -> Extraction
-> Cleaning -> Normalization -> Privacy/filtering -> Exact/semantic dedup
-> Quality -> Train/validation/test isolation -> Model-specific tokenization
-> Dataset shard validation -> Immutable authorized dataset release
-> Approved GPU job -> Checkpoint -> Independent evaluation
-> Model registry -> Canary release -> Controlled inference.

The independent evaluator needs its own trust boundary. Hidden test suites
must not be used for tuning. Dataset or rights withdrawal should have lineage
capable of identifying affected experiments and models.

Processing errors must quarantine/reject sources without silently admitting
them to the training pool. Future multimodal processors share provenance and
eligibility but keep their own media-specific extraction representations.
