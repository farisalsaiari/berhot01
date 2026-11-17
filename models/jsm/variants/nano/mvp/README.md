# JSM Nano MVP: Data Factory -> verified text -> tokenizer preview

**This is a real connected print-only smoke pipeline, NOT model training.**
It uses the shared BERHOT Data Factory, validates the published processed
candidate batch and runs a reversible UTF-8 byte tokenizer.

Data flow:
  explicit local source manifest
  -> services/data_factory/src/pipeline.py
  -> processed content-addressed text + immutable candidate manifest
  -> src/data_factory_bridge.py (revalidate SHA-256, paths, quality and rights)
  -> shared JSM byte tokenizer in models/jsm/src/tokenization/tokenizer.py
  -> terminal print: sample token IDs, token counts, status
  -> **train-ready dataset release BLOCKED** (rights not independently approved)
  -> **model weights and checkpoints NOT touched**

## Windows PowerShell (repository root)

    cd C:\Users\HeeMe\OneDrive\Desktop\berhot01
    python -m models.jsm.variants.nano.mvp.scripts.data_pipeline paths
    python -m models.jsm.variants.nano.mvp.scripts.data_pipeline smoke
    python -m unittest discover -s tests -p "test_jsm_nano_mvp_bridge.py" -v

For a real **already published** Data Factory processed manifest:

    python -m models.jsm.variants.nano.mvp.scripts.data_pipeline preview --manifest storage/data/manifests/local-text/YOUR_BATCH.json

If you use BERHOT_STORAGE_DIR or --storage-root to locate external storage,
pass the same root used when Data Factory published the manifest.

The smoke command uses synthetic Arabic/English examples and writes only to
a temporary disposable directory. The preview command reads existing
processed objects and writes zero files. No external models or tokenizers.

Tokenization is byte-level and deterministic (vocab size 259), **not a
trained Arabic-English BPE**. An actual future training tokenizer must be
versioned and recorded in approved dataset manifests.

## How a future approved training-ready handoff should work

A separate verified authorization/release process must confirm training
rights, build isolated train/validation/test shards, pin source+tokenizer
hashes and publish immutable datasets under
storage/data/datasets/jsm/<batch-id>/ before GPU training. This MVP
demonstrates the dependency chain without making a false authorization.
