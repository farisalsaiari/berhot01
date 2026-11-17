"""Reserved model operations. Never claim execution without a real backend."""
from .common import show, unavailable

PLANNED_FAMILIES = (
    "jsm", "fann", "nabra", "bahr", "edrak", "sora_provisional"
)


def configure(parent) -> None:
    actions = parent.add_subparsers(dest="model_action", required=True)
    items = actions.add_parser("list", help="List families named in the architecture (not available models)")
    items.set_defaults(handler=_list)
    train = actions.add_parser("train", help="RESERVED: controlled neural training")
    train.add_argument("--model", required=True)
    train.add_argument("--config", required=True)
    train.add_argument("--dataset", required=True)
    train.add_argument("--tokenizer")
    train.set_defaults(handler=_blocked)
    evaluate = actions.add_parser("evaluate", help="RESERVED: independent model evaluation")
    evaluate.add_argument("--run", required=True)
    evaluate.set_defaults(handler=_blocked)
    infer = actions.add_parser("infer", help="RESERVED: approved checkpoint inference")
    infer.add_argument("--model", required=True)
    infer.add_argument("--prompt")
    infer.set_defaults(handler=_blocked)
    post = actions.add_parser("posttrain", help="RESERVED: checkpoint-safe post-training")
    post.add_argument("--model", required=True)
    post.add_argument("--config", required=True)
    post.set_defaults(handler=_blocked)
    register = actions.add_parser("register", help="RESERVED: reviewed model promotion")
    register.add_argument("--run", required=True)
    register.set_defaults(handler=_blocked)


def _list(args) -> int:
    show({
        "operation": "model.list",
        "status": "ARCHITECTURE_ONLY",
        "planned_families": list(PLANNED_FAMILIES),
        "available_trained_models": [],
        "neural_training_implemented": False,
        "model_inference_implemented": False,
        "note": "This is a folder taxonomy, not a scan of verified checkpoints.",
    })
    return 0


def _blocked(args) -> int:
    why = {
        "train": "No approved dataset-release gate or production model trainer is connected to the universal CLI.",
        "evaluate": "No independently secured model evaluator is wired to the universal CLI.",
        "infer": "No registered approved model checkpoint or serving runtime is wired.",
        "posttrain": "No versioned SFT/preference trainer, approval gate or new checkpoint lineage is implemented.",
        "register": "No authenticated model registry with review, release promotion and rollback is implemented.",
    }
    return unavailable("model." + args.model_action, why[args.model_action])
