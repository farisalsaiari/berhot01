"""Unicode normalization for derived text, never modify source originals."""
import unicodedata


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be str")
    return unicodedata.normalize("NFC", text)
