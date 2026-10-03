from desk.judge_skip import (
    assemble_fields,
    evaluate_or_skip,
    evaluate_with_tool,
    explain,
    is_valid_tool_code,
    void_queue_offset,
)


def on_judge(offset_um: int) -> str:
    return evaluate_or_skip(offset_um)


def on_judge_with_tool(tool_code: str, offset_um: int) -> str:
    """带刀号判定：刀号合法才下结论，允差内合格、超出超差。"""
    return evaluate_with_tool(tool_code, offset_um)


def on_tool_valid(tool_code: str) -> bool:
    return is_valid_tool_code(tool_code)


def on_assemble(tool_code: str, offset_um: int, verdict: str) -> dict:
    packed = assemble_fields(tool_code, offset_um, verdict)
    # 队列与详情同源，真实刀补值在任何结论路径下都必须保留。
    packed["offset_um"] = void_queue_offset(packed["offset_um"], packed["verdict"])
    return packed


def note() -> str:
    return explain()
