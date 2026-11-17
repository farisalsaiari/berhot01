"""Text-only extraction for the local MVP.

Future PDF/DOCX/audio/video/3D extractors must be separate, sandboxed adapters.
"""


def extract_text(decoded_utf8: str) -> str:
    if not isinstance(decoded_utf8, str) or not decoded_utf8.strip():
        raise ValueError("Nothing to extract")
    return decoded_utf8
