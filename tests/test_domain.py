import json
import tempfile
import unittest
from unittest.mock import patch
from app.domain import DEMO, process
from app.runtime import Store


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(self.temp.name + "/test.db")
        self.case = process(DEMO, self.store)

    def tearDown(self):
        self.store.connection.close()
        self.temp.cleanup()

    def call(self, action, **kwargs):
        return process(dict(action=action, case_id=self.case["case_id"], **kwargs), self.store)

    def test_creation_is_minimal_and_planned(self):
        self.assertEqual(self.case["state"], "planned")
        self.assertEqual(self.case["progress"], {"completed": 0, "total": 5})

    def test_duplicate_does_not_create_another_case(self):
        result = process(DEMO, self.store)
        self.assertTrue(result["duplicate"])
        self.assertEqual(result["case_id"], self.case["case_id"])

    def test_conflicting_employee_reference_rejected(self):
        with self.assertRaises(ValueError):
            process(dict(DEMO, role="sales"), self.store)

    def test_extra_personal_data_rejected(self):
        with self.assertRaises(ValueError):
            process(dict(DEMO, employee_ref="EMP-NEW", email="person@example.test"), self.store)

    def test_dependencies_block_provisioning(self):
        self.call("activate")
        self.call("approve", task_id="account_provisioned", actor="manager-01")
        with self.assertRaises(ValueError):
            self.call("complete", task_id="account_provisioned", actor="it-01")

    def test_approval_required_even_after_dependencies(self):
        self.call("activate")
        for task in ("policy_acknowledged", "identity_verified"):
            self.call("complete", task_id=task, actor="hr-01")
        with self.assertRaises(ValueError):
            self.call("complete", task_id="account_provisioned", actor="it-01")

    def test_all_tasks_move_case_to_completed(self):
        self.call("activate")
        for task in ("policy_acknowledged", "identity_verified"):
            self.call("complete", task_id=task, actor="hr-01")
        self.call("approve", task_id="account_provisioned", actor="manager-01")
        self.call("complete", task_id="account_provisioned", actor="it-01")
        self.call("complete", task_id="workspace_ready", actor="it-01")
        self.call("approve", task_id="repository_access", actor="manager-01")
        final = self.call("complete", task_id="repository_access", actor="it-01")
        self.assertEqual(final["state"], "completed")
        self.assertEqual(final["progress"]["completed"], 5)
        audit_count = self.store.metrics()["audit_events"]
        repeated = self.call("complete", task_id="repository_access", actor="it-01")
        self.assertTrue(repeated["duplicate"])
        self.assertEqual(repeated["state"], "completed")
        self.assertEqual(self.store.metrics()["audit_events"], audit_count)

    def test_repeated_completion_is_idempotent(self):
        self.call("activate")
        self.call("complete", task_id="identity_verified", actor="hr-01")
        repeated = self.call("complete", task_id="identity_verified", actor="hr-01")
        self.assertTrue(repeated["duplicate"])
        self.assertEqual(repeated["progress"]["completed"], 1)

    def test_cancelled_case_rejects_task_mutation(self):
        self.call("cancel", reason="Solicitud retirada")
        event = self.store.connection.execute("SELECT data FROM events WHERE kind='onboarding_cancel'").fetchone()
        self.assertEqual(json.loads(event[0])["reason"], "Solicitud retirada")
        with self.assertRaises(ValueError):
            self.call("complete", task_id="identity_verified", actor="hr-01")

    def test_business_day_deadline_skips_weekend(self):
        result = process(dict(DEMO, employee_ref="EMP-FRIDAY", start_date="2026-10-23"), self.store)
        self.assertEqual(result["tasks"]["account_provisioned"]["due_date"], "2026-10-26")

    def test_role_specific_tasks(self):
        result = process(dict(DEMO, employee_ref="EMP-SALES", role="sales"), self.store)
        self.assertNotIn("repository_access", result["tasks"])

    def test_no_execution_before_activation(self):
        with self.assertRaises(ValueError):
            self.call("complete", task_id="identity_verified", actor="hr-01")

    def test_local_summary_uses_authoritative_state(self):
        result = self.call("summary")
        self.assertIn("planned", result["summary"])
        self.assertEqual(result["authoritative_state"]["progress"]["completed"], 0)

    def test_model_receives_no_employee_reference_and_cannot_mutate_state(self):
        with patch.dict("os.environ", {"MODEL_BACKEND": "ollama"}), patch("app.providers.generate", return_value="Resumen redactado") as generate:
            result = self.call("summary")
        self.assertNotIn(self.case["employee_ref"], generate.call_args.args[0])
        self.assertEqual(result["authoritative_state"]["state"], "planned")
        self.assertEqual(self.call("status")["state"], "planned")

    def test_weekend_start_moves_zero_day_deadline_to_monday(self):
        result = process(dict(DEMO, employee_ref="EMP-SATURDAY", start_date="2026-10-24"), self.store)
        self.assertEqual(result["tasks"]["identity_verified"]["due_date"], "2026-10-26")

    def test_compact_iso_date_rejected(self):
        with self.assertRaises(ValueError):
            process(dict(DEMO, employee_ref="EMP-BAD-DATE", start_date="20261026"), self.store)


if __name__ == "__main__":
    unittest.main()
