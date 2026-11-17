"""BERHOT universal operator CLI.

Command registration and routing only; underlying implementations live in
Data Factory and model packages. Unsupported operations fail closed.
"""
import argparse
import sys

from .commands import data, tokenizer, model, pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m berhot",
        description="BERHOT company CLI: real local Data Factory + JSM Nano preview; future AI commands explicitly reserved",
    )
    groups = parser.add_subparsers(dest="group", required=True)
    for name, implementation, help_text in (
        ("data", data, "Inspect and process explicitly selected source batches"),
        ("pipeline", pipeline, "Orchestrate Data Factory -> selected model preview"),
        ("tokenizer", tokenizer, "JSM UTF-8 tokenizer inspect, encode and candidate preview"),
        ("model", model, "Model-family registry and reserved train/eval/infer/posttrain commands"),
    ):
        parent = groups.add_parser(name, help=help_text)
        implementation.configure(parent)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (OSError, ValueError, PermissionError) as exc:
        print(f"[BERHOT ERROR] {exc}", file=sys.stderr)
        return 2
