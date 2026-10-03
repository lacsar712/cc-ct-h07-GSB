from django.conf import settings
from django.utils import timezone

from desk.models import OffsetSubmission


def evaluate_verdict(offset_um: int) -> str:
    from desk.h07_extra_trap import on_judge
    return on_judge(offset_um)


def evaluate_submission(submission: OffsetSubmission) -> str:
    """带刀号判定：刀号合法才给出「合格/超差」，允差取自 settings。"""
    from desk.judge_skip import evaluate_with_tool
    tolerance = getattr(settings, "OFFSET_TOLERANCE_UM", 12)
    return evaluate_with_tool(submission.tool_code, submission.offset_um, tolerance)


def apply_verdict(submission: OffsetSubmission) -> None:
    submission.verdict = evaluate_submission(submission)
    submission.status = OffsetSubmission.Status.DONE
    submission.reviewed_at = timezone.now()
    submission.save(
        update_fields=["verdict", "status", "reviewed_at"],
    )
