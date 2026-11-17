"""JSM tokenizer facade. Previews are real; training/BPE are not."""
from core.paths import STORAGE_DIR
from models.jsm.src.tokenization.tokenizer import JSMByteTokenizer
from models.jsm.variants.nano.mvp.src.tokenization_preview import (
    preview_candidate_batch, format_preview,
)
from models.jsm.variants.nano.mvp.scripts.data_pipeline import _smoke
from .common import show, unavailable


def configure(parent) -> None:
    actions = parent.add_subparsers(dest="tokenizer_action", required=True)
    meta = actions.add_parser("inspect", help="Show current available JSM tokenizer metadata")
    meta.add_argument("--family", default="jsm")
    meta.set_defaults(handler=_inspect)

    encode = actions.add_parser("encode", help="Reversibly encode a supplied text string")
    encode.add_argument("--family", default="jsm")
    encode.add_argument("--text", required=True)
    encode.add_argument("--show-tokens", type=int, default=64)
    encode.set_defaults(handler=_encode)

    preview = actions.add_parser("preview", help="Read-only token preview of a verified factory candidate batch")
    preview.add_argument("--family", default="jsm")
    preview.add_argument("--variant", default="nano")
    preview.add_argument("--size", default="mvp")
    preview.add_argument("--manifest", required=True)
    preview.add_argument("--storage-root", default=str(STORAGE_DIR))
    preview.add_argument("--show-tokens", type=int, default=12)
    preview.set_defaults(handler=_preview)

    smoke = actions.add_parser("smoke", help="Real Data Factory -> JSM tokenizer synthetic smoke")
    smoke.set_defaults(handler=_smoke_handler)

    train = actions.add_parser("train", help="RESERVED: learn a tokenizer from approved text (blocked)")
    train.add_argument("--family", required=True)
    train.add_argument("--dataset", required=True)
    train.set_defaults(handler=_train)


def _check_family(family: str) -> None:
    if family != "jsm":
        raise ValueError("Only JSM's reversible byte tokenizer is implemented; other families require dedicated representation/tokenization.")


def _inspect(args) -> int:
    _check_family(args.family)
    tok = JSMByteTokenizer()
    show({
        "operation": "tokenizer.inspect",
        "tokenizer_id": tok.tokenizer_id,
        "tokenizer_kind": "utf8_bytes_reversible_not_trained_bpe",
        "vocab_size": tok.vocab_size,
        "bos_token_id": tok.bos_token_id,
        "eos_token_id": tok.eos_token_id,
        "training_available": False,
        "model_weights_changed": False,
    })
    return 0


def _encode(args) -> int:
    _check_family(args.family)
    if not 0 <= args.show_tokens <= 1000:
        raise ValueError("--show-tokens must be between 0 and 1000")
    tok = JSMByteTokenizer()
    ids = tok.encode(args.text)
    if tok.decode(ids) != args.text:
        raise ValueError("Tokenizer round-trip mismatch")
    show({
        "operation": "tokenizer.encode",
        "tokenizer_id": tok.tokenizer_id,
        "token_count": len(ids),
        "first_token_ids": ids[:args.show_tokens],
        "decode_round_trip_ok": True,
        "data_written": False,
    })
    return 0


def _preview(args) -> int:
    _check_family(args.family)
    if (args.variant, args.size) != ("nano", "mvp"):
        return unavailable(
            "tokenizer.preview",
            "Only jsm/nano/mvp has the Data Factory candidate-preview bridge. Other variants require an explicit adapter."
        )
    print(format_preview(preview_candidate_batch(
        args.manifest, args.storage_root, show_tokens=args.show_tokens
    )))
    return 0


def _smoke_handler(args) -> int:
    report = _smoke()
    show({
        "operation": "tokenizer.smoke",
        "status": "PASSED_CANDIDATE_PREVIEW",
        "batch_id": report["preview"]["batch_id"],
        "verified_sources": report["preview"]["verified_sources"],
        "tokenizer": report["preview"]["tokenizer"],
        "total_preview_tokens": report["preview"]["total_preview_tokens"],
        "train_ready_export": report["preview"]["train_ready_export"],
        "no_model_training": True,
    })
    return 0


def _train(args) -> int:
    return unavailable(
        "tokenizer.train",
        "Training a new JSM BPE/audio/3D tokenizer requires a separately approved frozen training dataset and a versioned tokenizer trainer. Neither is implemented."
    )
