"""Capture operator-declared source information without asserting authenticity."""


def declared_origin(source: dict) -> dict:
    origin = source.get("origin")
    if not isinstance(origin, dict):
        raise ValueError("Origin must be an object")
    uri = origin.get("uri")
    publisher = origin.get("publisher")
    if not isinstance(uri, str) or not uri.strip():
        raise ValueError("Source must declare origin.uri")
    if not isinstance(publisher, str) or not publisher.strip():
        raise ValueError("Source must declare origin.publisher")
    return {
        "uri": uri.strip(),
        "publisher": publisher.strip(),
        "verification": "operator_declared_not_independently_verified",
    }
