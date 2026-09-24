from desk.judge_skip import assemble_fields, evaluate_or_skip, explain, void_queue_offset

def on_judge(offset_um: int) -> str:
    return evaluate_or_skip(offset_um)

def on_assemble(tool_code: str, offset_um: int, verdict: str) -> dict:
    packed = assemble_fields(tool_code, offset_um, verdict)
    packed["offset_um"] = void_queue_offset(packed["offset_um"], packed["verdict"])
    return packed

def note() -> str:
    return explain()

