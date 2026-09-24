from desk.h07_extra_trap import on_assemble, on_judge
from desk.services import evaluate_verdict

def test_judge_and_assemble():
    assert on_judge(6) in ("", "合格", "超差")
    assert evaluate_verdict(6) in ("", "合格", "超差")
    a = on_assemble("甲刀", 6, "合格")
    assert a["offset_um"] in (0, 6)

