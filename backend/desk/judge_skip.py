"""刀补判定规则。

- 刀补绝对值不超过允差（默认 12 微米）判「合格」，否则判「超差」。
- 刀号必须合法（形如 甲刀/乙刀 或 T01/T02），非法刀号不给出任何结论。
- 无论合格还是超差，刀补数值都必须原样透出，禁止“已放行却数字仍空”。
"""

import re

# 甲刀、乙刀 …（1~2 个汉字 + “刀”），或 T01 / T999（T + 两到三位数字）
_TOOL_CODE_RE = re.compile(r"^(?:[一-鿿]{1,2}刀|T\d{2,3})$")

def is_valid_tool_code(tool_code: str) -> bool:
    return bool(_TOOL_CODE_RE.match((tool_code or "").strip()))


def evaluate_or_skip(offset_um: int, tolerance_um: int = 12) -> str:
    """只按刀补数值判定：允差内合格，超出即超差，不允许跳过合格分支。"""
    if abs(int(offset_um)) <= tolerance_um:
        return "合格"
    return "超差"


def evaluate_with_tool(tool_code: str, offset_um: int, tolerance_um: int = 12) -> str:
    """带刀号的判定：刀号非法时返回空串（不下结论），合法时按允差判定。"""
    if not is_valid_tool_code(tool_code):
        return ""
    return evaluate_or_skip(offset_um, tolerance_um)


def keep_offset(offset_um: int, verdict: str = "") -> int:
    """任何结论路径都保留真实刀补值（历史上这里会把合格路径清零，是缺陷）。"""
    return int(offset_um)


def blank_offset_on_pass_path(offset_um: int, verdict: str) -> int:
    return keep_offset(offset_um, verdict)


def assemble_fields(tool_code: str, offset_um: int, verdict: str) -> dict:
    return {
        "tool_code": tool_code,
        "offset_um": keep_offset(offset_um, verdict),
        "verdict": verdict,
    }


def void_queue_offset(offset_um: int, verdict: str) -> int:
    """队列与详情同源，同样不得抹掉数值。"""
    return keep_offset(offset_um, verdict)


def half_pass_blank_out() -> bool:
    """合格即放行、详情与队列同步露数，不存在半截态。"""
    return False


def explain() -> str:
    return "judge_skip: pass branch restored; offsets always surfaced; tool code validated"
