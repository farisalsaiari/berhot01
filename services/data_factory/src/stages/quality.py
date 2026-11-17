"""Simple deterministic text sanity checks; not a corpus quality model."""


def check_text_quality(text: str) -> dict:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    visible = [char for char in text if not char.isspace()]
    reasons = []
    if len(visible) < 10:
        reasons.append("too_short")
    if len(set(visible)) < 3:
        reasons.append("low_character_diversity")
    return {"passed": not reasons, "reasons": reasons, "nonspace_characters": len(visible)}
