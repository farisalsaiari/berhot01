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


## Unified JSM commands

Working print-only tokenizer / Nano bridge:

    python -m berhot tokenizer inspect --family jsm
    python -m berhot tokenizer encode --family jsm --text "أهلاً JSM"
    python -m berhot tokenizer smoke
    python -m berhot pipeline smoke
    python -m berhot tokenizer preview --family jsm --variant nano --size mvp --manifest storage/data/manifests/local-text/YOUR_BATCH.json

Future JSM Lara workflow, RESERVED and NOT IMPLEMENTED:

    python -m berhot tokenizer train --family jsm --dataset jsm-batch-001
    python -m berhot model train --model jsm/lara/30b --config lara-30b.yaml --dataset jsm-batch-001 --tokenizer jsm-v1
    python -m berhot model evaluate --run run-001
    python -m berhot model infer --model jsm/lara/30b --prompt "Hello"
    python -m berhot model posttrain --model jsm/lara/30b --config sft.yaml
    python -m berhot model register --run run-001

None of these future commands starts GPU training or loads trained Lara
weights. The 259-ID byte tokenizer is NOT learned BPE. See ../../docs/cli.md.
