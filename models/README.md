# BERHOT model families

JSM (language), FANN (3D), Nabra (voice), Bahr (video/motion),
Edrak (robotics), and a future image-generation model. Models own
architecture, training, inference and model-specific tokenization;
shared data ingestion, APIs, identity and registry remain outside models/.
Only JSM currently has a source scaffold. No weights or working model
server exist in this tracked repository.


## Shared operator command style

Use the company CLI; actual model trainers will live under each family:

    python -m berhot model list
    python -m berhot pipeline smoke

Future commands (NOT IMPLEMENTED, return nonzero, no model writes):

    python -m berhot model train --model jsm/lara/30b --config lara.yaml --dataset jsm-batch-001
    python -m berhot model train --model fann/base --config fann-base.yaml --dataset fann-batch-001
    python -m berhot model evaluate --run run-001
    python -m berhot model infer --model jsm/lara/30b --prompt "Hello"
    python -m berhot model posttrain --model jsm/lara/30b --config sft.yaml

Future FANN/Nabra/Bahr/robotics backends have different media-specific
data encoders; they are NOT automatically wired by the current text MVP.
See ../docs/cli.md.
