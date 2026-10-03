from django.test import TestCase
from ninja.testing import TestClient

from desk.api import api
from desk.auth_utils import create_access_token, hash_password
from desk.models import OffsetSubmission, User
from desk.services import apply_verdict, evaluate_verdict
from desk.judge_skip import half_pass_blank_out
from desk.h07_extra_trap import on_assemble, on_judge, on_judge_with_tool


class VerdictTests(TestCase):
    def test_within_tolerance_is_pass(self):
        # 交 6 微米、交 2 微米都必须判合格（此前合格分支被跳过）
        self.assertEqual(on_judge(6), "合格")
        self.assertEqual(on_judge(2), "合格")
        self.assertEqual(on_judge(12), "合格")       # 边界含 12
        self.assertEqual(on_judge(-6), "合格")      # 绝对值
        self.assertEqual(evaluate_verdict(2), "合格")

    def test_over_tolerance_is_fail(self):
        # 乙刀继续超差
        self.assertEqual(on_judge(13), "超差")
        self.assertEqual(on_judge(20), "超差")
        self.assertEqual(on_judge(-20), "超差")

    def test_tool_code_gate(self):
        self.assertEqual(on_judge_with_tool("甲刀", 6), "合格")
        self.assertEqual(on_judge_with_tool("甲刀", 2), "合格")
        self.assertEqual(on_judge_with_tool("T01", 5), "合格")
        self.assertEqual(on_judge_with_tool("乙刀", 20), "超差")
        # 刀号不合法不下结论
        self.assertEqual(on_judge_with_tool("乱码刀号", 6), "")
        self.assertEqual(on_judge_with_tool("T1", 6), "")
        self.assertEqual(on_judge_with_tool("", 6), "")

    def test_no_half_released_blank_state(self):
        # 不允许“已放行却数字仍空”
        self.assertIs(half_pass_blank_out(), False)


class AssembleNumberVisibleTests(TestCase):
    def _assert_number_kept(self, tool, offset, verdict):
        packed = on_assemble(tool, offset, verdict)
        self.assertEqual(packed["verdict"], verdict)
        self.assertEqual(packed["offset_um"], offset)  # 不得清零

    def test_pass_keeps_number_in_queue_and_detail(self):
        # 队列表与详情都走 on_assemble，两处都必须露出真实数值
        self._assert_number_kept("甲刀", 6, "合格")
        self._assert_number_kept("甲刀", 2, "合格")

    def test_fail_keeps_number(self):
        self._assert_number_kept("乙刀", 20, "超差")


class EndToEndFlowTests(TestCase):
    def setUp(self):
        self.machinist = User.objects.create(
            username="machinist",
            password=hash_password("machine123456"),
            role=User.Role.MACHINIST,
        )
        self.token = create_access_token(self.machinist)
        self.client = TestClient(api)
        self.auth = {"Authorization": f"Bearer {self.token}"}

    def _release(self, tool, offset):
        row = OffsetSubmission.objects.create(
            tool_code=tool, offset_um=offset,
            submitted_by=self.machinist,
            status=OffsetSubmission.Status.PENDING,
        )
        apply_verdict(row)
        row.refresh_from_db()
        return row

    def test_jia_release_shows_number_both_places(self):
        row = self._release("甲刀", 6)
        self.assertEqual(row.status, OffsetSubmission.Status.DONE)
        self.assertEqual(row.verdict, "合格")
        self.assertEqual(row.offset_um, 6)

        # 队列（列表）
        listing = self.client.get("/submissions", headers=self.auth).json()
        queue = next(r for r in listing if r["id"] == row.id)
        self.assertEqual(queue["verdict"], "合格")
        self.assertEqual(queue["offset_um"], 6)

        # 详情
        detail = self.client.get(f"/submissions/{row.id}", headers=self.auth).json()
        self.assertEqual(detail["verdict"], "合格")
        self.assertEqual(detail["offset_um"], 6)

    def test_two_um_pass_shows_number_both_places(self):
        row = self._release("甲刀", 2)
        self.assertEqual(row.verdict, "合格")
        self.assertEqual(row.offset_um, 2)
        listing = self.client.get("/submissions", headers=self.auth).json()
        detail = self.client.get(f"/submissions/{row.id}", headers=self.auth).json()
        self.assertEqual(next(r for r in listing if r["id"] == row.id)["offset_um"], 2)
        self.assertEqual(detail["offset_um"], 2)

    def test_yi_keeps_failing_with_number(self):
        row = self._release("乙刀", 20)
        self.assertEqual(row.verdict, "超差")
        self.assertEqual(row.offset_um, 20)
        detail = self.client.get(f"/submissions/{row.id}", headers=self.auth).json()
        self.assertEqual(detail["verdict"], "超差")
        self.assertEqual(detail["offset_um"], 20)

    def test_invalid_tool_code_rejected(self):
        resp = self.client.post(
            "/submissions",
            json={"tool_code": "乱码刀号", "offset_um": 6},
            headers=self.auth,
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(OffsetSubmission.objects.count(), 0)
