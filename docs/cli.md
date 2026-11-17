# BERHOT universal CLI: operator commands and status

From the BERHOT repository root, the unified entry point is:

    python -m berhot <group> <action> [flags]

After running python -m pip install -e . you may also use the shorter
berhot command. Prefer python -m berhot to select the active interpreter.

## Implemented TODAY (local-only)

| Command | Current effect |
| --- | --- |
| python -m berhot data smoke | Disposable synthetic Data Factory test |
| python -m berhot data inspect --manifest FILE --intake-root DIR | Validate exact listed UTF-8 files, no writes |
| python -m berhot data process --manifest FILE --intake-root DIR | Publish processed candidate text + immutable manifest |
| python -m berhot data eligibility --manifest PUBLISHED_FILE | Report NOT train-ready; no independent rights approval |
| python -m berhot pipeline smoke | Synthetic Data Factory -> JSM Nano tokenizer smoke |
| python -m berhot pipeline run --manifest FILE --intake-root DIR | Process real selected text and preview JSM Nano tokens |
| python -m berhot tokenizer inspect --family jsm | Current reversible tokenizer ID and vocabulary |
| python -m berhot tokenizer encode --family jsm --text TEXT | Print reversible UTF-8 byte token IDs and count |
| python -m berhot tokenizer preview --manifest PUBLISHED_FILE | Verify processed candidate + print token counts |
| python -m berhot model list | Print planned family taxonomy, not live models |

The tokenizer is a 259-token reversible UTF-8 byte mapping, NOT
trained Arabic/English BPE. It does not involve PyTorch or train weights.

## Future commands REGISTERED but NOT IMPLEMENTED

These return status NOT_IMPLEMENTED and exit code 2, without executing
training or releasing data:

    python -m berhot data publish --batch batch-000001 --family jsm
    python -m berhot tokenizer train --family jsm --dataset jsm-batch-000001
    python -m berhot model train --model jsm/lara/30b --config lara-30b.yaml --dataset jsm-batch-000001 --tokenizer jsm-v1
    python -m berhot model train --model fann/base --config fann-base.yaml --dataset fann-batch-000001
    python -m berhot model evaluate --run run-000001
    python -m berhot model infer --model jsm/lara/30b --prompt "Hello"
    python -m berhot model posttrain --model jsm/lara/30b --config sft.yaml
    python -m berhot model register --run run-000001

Until they have approved model/dataset backends, these commands cannot
publish training-ready shards, create model weights or claim evaluation.

## Windows PowerShell: verify a new installation

    cd C:\Users\HeeMe\OneDrive\Desktop\berhot01
    python -m pip install -e .
    python -m berhot --help
    python -m berhot data --help
    python -m berhot data smoke
    python -m berhot pipeline smoke
    python -m berhot tokenizer inspect --family jsm
    python -m berhot tokenizer encode --family jsm --text "أهلاً BERHOT"
    python -m berhot model list
    python -m unittest discover -s tests -v

Both smoke commands use TEMPORARY SYNTHETIC documents, not real intake.

## Windows PowerShell: ingest a new permitted UTF-8 .txt source

Put new-document.txt into intake/berhot/ locally. You must have permission
to retain/analyze it; do not commit confidential intake into Git.

Create a canonical SHA-256-pinned manifest using PowerShell.
This writes JSON as UTF-8 WITHOUT BOM (works in Windows PowerShell 5/7):

    $file = ".\intake\berhot\new-document.txt"
    $sha = (Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant()
    $manifest = @{
      schema_version = "1.0.0"
      batch_id = "berhot-batch-000001"
      sources = @(@{
        source_id = "berhot-doc-001"
        relative_path = "berhot/new-document.txt"
        sha256 = $sha
        origin = @{
          uri = "internal://berhot/new-document"
          publisher = "BERHOT"
        }
        rights = @{
          retention_allowed = $true
          analysis_allowed = $true
          training_allowed = $false
        }
      })
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText(
      (Join-Path (Get-Location) "new-batch.json"),
      ($manifest | ConvertTo-Json -Depth 8),
      $utf8
    )

1. Inspect ONLY the files listed in the manifest (no output written):

       python -m berhot data inspect --manifest .\new-batch.json --intake-root .\intake

2. Publish immutable processed CANDIDATE text (not training data):

       python -m berhot data process --manifest .\new-batch.json --intake-root .\intake

3. Query its non-training authorization status:

       python -m berhot data eligibility --family jsm --manifest .\storage\data\manifests\local-text\berhot-batch-000001.json

4. Preview tokenization of the canonical factory output:

       python -m berhot tokenizer preview --family jsm --variant nano --size mvp --manifest .\storage\data\manifests\local-text\berhot-batch-000001.json

Alternatively, process the selected manifest and preview JSM Nano
token IDs in ONE real executable command:

    python -m berhot pipeline run --manifest .\new-batch.json --intake-root .\intake --family jsm --variant nano --size mvp

All commands should run from the repository root. If you use
BERHOT_STORAGE_DIR or --storage-root, use the same root for Data Factory
and the subsequent tokenizer preview.

Use a NEW batch_id if source data or its metadata changes. Do not
overwrite published immutable manifests or auto-scan intake folders.

## Model architecture and artifact layout

The CLI routes commands; underlying implementation belongs to each family:

    berhot/                      CLI entrypoint and command adapters
    services/data_factory/       inspected source processing
    models/jsm/src/tokenization/  JSM tokenizer algorithm
    models/jsm/variants/nano/mvp/ read-only candidate preview bridge
    models/jsm/src/training/      future JSM trainer
    models/fann/                  future FANN geometry data and trainer
    services/model_registry/      future approved releases

Filesystem conventions:

    storage/data/processed/text-sha256/<digest>.txt
    storage/data/manifests/local-text/<batch-id>.json
    storage/data/datasets/jsm/<batch-id>/       FUTURE train-ready dataset
    storage/data/datasets/fann/<batch-id>/      FUTURE 3D dataset
    storage/artifacts/jsm/tokenizers/<version>/ FUTURE learned tokenizer
    storage/artifacts/jsm/lara/30b/runs/<run-id>/ FUTURE neural runs
    storage/artifacts/fann/<variant>/...        FUTURE FANN neural runs
    storage/releases/<family>/                  FUTURE approved releases

Model training should use frozen approved datasets, training-only
tokenizer fitting, pinned tokenizer/dataset hashes, immutable run configs,
and independent evaluation with sealed holdouts.

Each family uses its own media processors: 3D geometry and UV maps for
FANN, waveform/speech for Nabra, video motion for Bahr, etc. Current
Data Factory is text-only and is NOT a PDF, DOCX, audio, video or 3D extractor.

## Status codes and safety

Implemented successful operations return exit status 0. Missing/invalid
inputs and all future unavailable operations return nonzero (typically 2).
The local Data Factory demands declared retention and analysis rights,
but its source declarations are NOT independent legal verification.
It explicitly rejects training_allowed=true and it never creates
training-ready datasets, GPUs jobs or production releases.
