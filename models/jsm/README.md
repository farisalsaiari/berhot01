## Setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# python -m pip install -e models/jsm/variants/nano/mvp
cd models/jsm
```

## Inspect the data and model

Run these commands from the MVP directory:

```bash
python -m scripts.ingestion
python -m scripts.tokenizer
python -m scripts.dataset
python -m scripts.model
```