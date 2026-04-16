"""Label mapping utility scaffold.

Implement in feature/units-labels.
"""


def label_for_variable(raw_name: str, advanced: bool = False) -> str:
    """Map raw variable names to plain-English labels (minimal bootstrap behavior)."""
    return raw_name if advanced else raw_name.replace("_", " ").title()
