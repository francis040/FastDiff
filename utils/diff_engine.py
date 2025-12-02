import difflib
from typing import List, Tuple, Dict, Any


LineInfo = Dict[str, Any]
Row = Dict[str, Any]


_DEF_EMPTY = ""


def _char_differences(left: str, right: str) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Return ranges of differing characters for left and right strings."""
    left_ranges: List[Tuple[int, int]] = []
    right_ranges: List[Tuple[int, int]] = []
    matcher = difflib.SequenceMatcher(None, left, right)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if i1 != i2:
            left_ranges.append((i1, i2))
        if j1 != j2:
            right_ranges.append((j1, j2))
    return left_ranges, right_ranges


def generate_diff(left_text: str, right_text: str) -> Tuple[List[Row], int]:
    """
    Generate a structured diff between two text blocks.

    Returns a tuple of (rows, diff_count) where rows is a list of dictionaries
    describing each aligned line for the left and right panes. diff_count
    represents how many rows contain differences.
    """
    left_lines = left_text.splitlines()
    right_lines = right_text.splitlines()

    matcher = difflib.SequenceMatcher(None, left_lines, right_lines)
    rows: List[Row] = []
    diff_count = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        left_chunk = left_lines[i1:i2]
        right_chunk = right_lines[j1:j2]

        if tag == "equal":
            for offset, line in enumerate(left_chunk):
                row: Row = {
                    "tag": tag,
                    "left": {"number": i1 + offset + 1, "text": line, "status": "context", "char_changes": []},
                    "right": {
                        "number": j1 + offset + 1,
                        "text": right_chunk[offset],
                        "status": "context",
                        "char_changes": [],
                    },
                }
                rows.append(row)
        else:
            max_len = max(len(left_chunk), len(right_chunk))
            for offset in range(max_len):
                left_line = left_chunk[offset] if offset < len(left_chunk) else _DEF_EMPTY
                right_line = right_chunk[offset] if offset < len(right_chunk) else _DEF_EMPTY
                left_number = i1 + offset + 1 if offset < len(left_chunk) else None
                right_number = j1 + offset + 1 if offset < len(right_chunk) else None

                left_changes: List[Tuple[int, int]] = []
                right_changes: List[Tuple[int, int]] = []

                if tag == "replace" and left_line and right_line:
                    left_changes, right_changes = _char_differences(left_line, right_line)

                status_map = {
                    "replace": "modified",
                    "delete": "deleted",
                    "insert": "added",
                }
                status = status_map.get(tag, "context")

                row = {
                    "tag": tag,
                    "left": {"number": left_number, "text": left_line, "status": status, "char_changes": left_changes},
                    "right": {"number": right_number, "text": right_line, "status": status, "char_changes": right_changes},
                }
                rows.append(row)
                diff_count += 1

    return rows, diff_count
