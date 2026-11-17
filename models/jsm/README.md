# BERHOT JSM model-family scaffold

JSM architecture, training, evaluation, inference, post-training and
tokenization folders are currently mostly EMPTY placeholder modules.
There is no tested model training command in this tracked repository.

For future production packaging prefer models/jsm/src/berhot_jsm/ with
installable package metadata. Keep variant-specific size/configuration
separate from shared family code. Do not silently migrate or modify
checkpoint-bound experiments in other repositories.

The previous JSM ingestion command referenced a missing module and is
now redirected to the shared local Data Factory CLI. From root:

    python -m models.jsm.scripts.ingestion smoke-local

The shared family tokenizer should be versioned at
storage/artifacts/jsm/tokenizers/<tokenizer-version>/.
Future runs belong under
storage/artifacts/jsm/<variant>/<size>/runs/<run-id>/.

See docs/architecture/repository-layout.md and docs/storage.md.
