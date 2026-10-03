"""H07: judge every submission; the real offset stays visible on all paths."""


def evaluate_or_skip(offset_um: int) -> str:
    """|offset| <= 12 µm → 合格, otherwise 超差. The pass branch is never skipped."""
    if abs(int(offset_um)) <= 12:
        return "合格"
    return "超差"


def preserve_offset(offset_um: int, verdict: str) -> int:
    """Offset is shown exactly as submitted, on pass and fail paths alike."""
    return int(offset_um)


def assemble_fields(tool_code: str, offset_um: int, verdict: str) -> dict:
    return {
        "tool_code": tool_code,
        "offset_um": preserve_offset(offset_um, verdict),
        "verdict": verdict,
    }


def void_queue_offset(offset_um: int, verdict: str) -> int:
    """Queue rows keep the same real offset as the detail view (never blanked)."""
    return preserve_offset(offset_um, verdict)


def half_pass_blank_out() -> bool:
    """Verdict and offset are released together; no half-released blank state."""
    return False


def explain() -> str:
    return "judge_skip: pass branch judged and offsets preserved on all paths"
