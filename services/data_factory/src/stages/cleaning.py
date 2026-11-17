"""Minimal conservative cleanup; retain content and meaningful lines."""


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip(" \t") for line in text.split("\n")).strip() + "\n"
