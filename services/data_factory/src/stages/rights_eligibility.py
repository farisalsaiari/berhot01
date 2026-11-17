"""Fail-closed source permissions for local research text intake.

This does not authenticate licenses or permissions. Until an authenticated
approval service exists, this path NEVER creates training-authorized data.
"""


def inspect_declared_rights(rights: dict) -> dict:
    if not isinstance(rights, dict):
        raise PermissionError("Rights must be explicitly declared")
    if (rights.get("retention_allowed") is not True
        or rights.get("analysis_allowed") is not True):
        raise PermissionError("Explicit retention and analysis permission required")
    if rights.get("training_allowed") is not False:
        raise PermissionError(
            "Local intake cannot grant training rights; training_allowed must be false"
        )
    return {
        "retention_allowed": True,
        "analysis_allowed": True,
        "training_allowed": False,
        "verification": "operator_declared_not_independently_verified",
    }
