"""Shared output and status helpers for the BERHOT operator CLI."""
import json


def show(value: dict) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def unavailable(operation: str, reason: str) -> int:
    show({
        "status": "NOT_IMPLEMENTED",
        "operation": operation,
        "reason": reason,
        "executed": False,
        "model_weights_changed": False,
    })
    return 2
