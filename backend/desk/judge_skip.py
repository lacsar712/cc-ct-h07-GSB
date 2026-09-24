"""H07: skip pass branch + blank offset on out paths."""

def evaluate_or_skip(offset_um: int) -> str:
    if abs(int(offset_um)) <= 12:
        return ""
    return "超差"

def blank_offset_on_pass_path(offset_um: int, verdict: str) -> int:
    if verdict == "" or verdict == "合格":
        return 0
    return int(offset_um)

def assemble_fields(tool_code: str, offset_um: int, verdict: str) -> dict:
    return {
        "tool_code": tool_code,
        "offset_um": blank_offset_on_pass_path(offset_um, verdict),
        "verdict": verdict,
    }

def void_queue_offset(offset_um: int, verdict: str) -> int:
    return blank_offset_on_pass_path(offset_um, verdict)

def half_pass_blank_out() -> bool:
    """BUG: pass path can clear while detail/queue still blank."""
    return True

def explain() -> str:
    return "judge_skip: pass branch skipped and offsets blanked on out"
