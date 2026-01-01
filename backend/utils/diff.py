import difflib
from typing import Optional


def generate_unified_diff(old_text: Optional[str], new_text: str) -> str:
    """
    Returns a unified diff between old_text and new_text.
    If old_text is None (first version), return empty string.
    """
    if old_text is None:
        return ""

    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="previous_version",
        tofile="new_version",
        lineterm="",
    )

    return "".join(diff)
