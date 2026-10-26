"""
PRODE Hermetic Unit & Integration Test Suite.
Runs 100% offline with an in-memory SQLite database (:memory:) and zero network calls.
"""

import unittest
from pathlib import Path

from prode.catalog import DEPARTMENTS, PROJECTS, REVENUE_ENGINES, ROLES, VERSIONS
from prode.db import ProdeDB
from prode.engine import (
    CashFlowLockViolation,
    ContractValidationError,
    ProdeEngine,
    SpendBoundaryViolation,
)
from prode.server import UI_HTML_PATH, dispatch_api_request


class TestProdeCompanyOS(unittest.TestCase):
    def setUp(self) -> None:
        self.db = ProdeDB(db_path=":memory:")
        self.engine = ProdeEngine(db=self.db)

    def tearDown(self) -> None:
        self.db.close()

    def test_01_nine_departments_and_69_roles_exact_distribution(self) -> None:
        self.assertEqual(len(DEPARTMENTS), 9)
        self.assertEqual(len(ROLES), 69)

        expected_counts = {
            "DEPT-01": 7,
            "DEPT-02": 8,
            "DEPT-03": 7,
            "DEPT-04": 9,
            "DEPT-05": 9,
            "DEPT-06": 8,
            "DEPT-07": 8,
            "DEPT-08": 7,
            "DEPT-09": 6,
        }
        db_depts = {d["id"]: d for d in self.db.get_departments()}
        self.assertEqual(len(db_depts), 9)

        for dept_id, count in expected_counts.items():
            roles_in_dept = self.db.get_roles(department_id=dept_id)
            self.assertEqual(
                len(roles_in_dept),
                count,
                f"Department {dept_id} expected {count} roles, got {len(roles_in_dept)}",
            )
            self.assertEqual(db_depts[dept_id]["role_count"], count)

    def test_02_five_versions_15_projects_30_milestones_90_tasks(self) -> None:
        self.assertEqual(len(REVENUE_ENGINES), 3)
        self.assertEqual(len(VERSIONS), 5)
        self.assertEqual(len(PROJECTS), 15)

        summary = self.engine.get_dashboard_summary()
        m = summary["metrics"]
        self.assertEqual(m["total_versions"], 5)
        self.assertEqual(m["total_projects"], 15)
        self.assertEqual(m["total_milestones"], 30)
        self.assertEqual(m["total_tasks"], 90)

        valid_role_ids = {r["id"] for r in ROLES}
        for ver in ["v1.0", "v2.0", "v3.0", "v4.0", "v5.0"]:
            v_projs = self.db.get_projects(version=ver)
            self.assertEqual(len(v_projs), 3, f"Version {ver} must have 3 projects")
            for p in v_projs:
                self.assertEqual(len(p["milestones"]), 2)
                for ms in p["milestones"]:
                    self.assertEqual(len(ms["tasks"]), 3)
                    for t in ms["tasks"]:
                        self.assertIn(t["assigned_role_id"], valid_role_ids)
                        self.assertIn(t["reviewer_role_id"], valid_role_ids)

    def test_03_hard_zero_dollar_spend_guard(self) -> None:
        res = self.engine.enforce_spend_guard(0.0, context="local_execution")
        self.assertEqual(res["status"], "ALLOWED")

        with self.assertRaises(SpendBoundaryViolation):
            self.engine.enforce_spend_guard(19.99, approved_by_owner=False, context="paid_api")

        res_override = self.engine.enforce_spend_guard(
            19.99, approved_by_owner=True, context="zak_approved_resource"
        )
        self.assertEqual(res_override["status"], "ALLOWED")

    def test_04_cash_flow_50_25_25_locks(self) -> None:
        # PROJ-V3-02 has contract_value_usd=42000.0 and deposit_50_cleared=False
        with self.assertRaises(CashFlowLockViolation):
            self.engine.enforce_engineering_start_lock("PROJ-V3-02")

        # Clear 50% deposit -> engineering unlocks, but IP handover still blocked
        self.engine.update_payment_milestone("PROJ-V3-02", "deposit_50", True)
        unlocked = self.engine.enforce_engineering_start_lock("PROJ-V3-02")
        self.assertTrue(unlocked["engineering_unlocked"])

        with self.assertRaises(CashFlowLockViolation):
            self.engine.enforce_ip_handover_lock("PROJ-V3-02")

        # Clear remaining 25% staging and 25% final -> IP handover unlocks
        self.engine.update_payment_milestone("PROJ-V3-02", "staging_25", True)
        self.engine.update_payment_milestone("PROJ-V3-02", "final_25", True)
        ip_res = self.engine.enforce_ip_handover_lock("PROJ-V3-02")
        self.assertTrue(ip_res["ip_handover_unlocked"])

    def test_05_opportunity_and_saas_spinout_validators(self) -> None:
        opp_pass = self.engine.validate_opportunity(50000.0, True, True, True, True)
        self.assertTrue(opp_pass["passed"])
        self.assertEqual(opp_pass["recommendation"], "PROCEED_TO_SPRINT_ZERO")

        opp_fail = self.engine.validate_opportunity(5000.0, True, False, True, True)
        self.assertFalse(opp_fail["passed"])

        saas_pass = self.engine.validate_saas_spinout(3, 0.75, 0.0, True)
        self.assertTrue(saas_pass["passed"])
        self.assertEqual(saas_pass["recommendation"], "APPROVED_FOR_V5_SAAS_SPINOUT")

        saas_fail = self.engine.validate_saas_spinout(1, 0.40, 5000.0, False)
        self.assertFalse(saas_fail["passed"])

    def test_06_designer_studio_codelift_triple_contract_qc(self) -> None:
        brief = {
            "id": "BRIEF-001",
            "owner": "designer",
            "intent": "Enterprise IoT & 3D Control Surface",
            "audience": "Technical Operators",
            "placement": "Primary Viewport",
            "composition": "12-column grid with 3D digital twin panel",
            "accessibility": "WCAG 2.2 AA (2.5.3 Label in Name, 3.3.2 Labels or Instructions)",
            "acceptance_criteria": "60 FPS + AA contrast in Light & Dark modes",
        }
        delivery = {
            "brief_id": "BRIEF-001",
            "owner": "studio",
            "asset_uri": "assets/iot-twin-render.png",
            "production_rationale": "50mm lens, key light 45deg, contact shadow verified",
            "rights": "PRODE_CORE_IP",
            "image_qc": {"owner": "studio", "reviewer": "QSR-04", "status": "pass", "findings": []},
            "design_fit_qc": {"owner": "designer", "reviewer": "QSR-03", "status": "pass", "findings": []},
            "ast_compile_qc": {"owner": "codelift", "reviewer": "SWE-09", "status": "pass", "findings": []},
        }
        res = self.engine.evaluate_designer_studio_codelift_contract(brief, delivery)
        self.assertTrue(res["accepted"])

        delivery["image_qc"]["owner"] = "designer"
        with self.assertRaises(ContractValidationError):
            self.engine.evaluate_designer_studio_codelift_contract(brief, delivery)

    def test_07_topological_dag_cycle_detection_and_full_simulation(self) -> None:
        cyclic_tasks = [
            {"id": "T1", "depends_on": ["T2"]},
            {"id": "T2", "depends_on": ["T1"]},
        ]
        with self.assertRaises(ContractValidationError):
            self.engine.topological_sort_tasks(cyclic_tasks)

        # Simulate all 15 projects across v1.0 -> v5.0
        for proj in self.db.get_projects():
            sim = self.engine.simulate_project(proj["id"], auto_clear_deposit=True)
            self.assertEqual(sim["status"], "COMPLETED")
            self.assertEqual(sim["tasks_executed"], 6)

        summary = self.engine.get_dashboard_summary()
        self.assertEqual(summary["metrics"]["completed_milestones"], 30)
        self.assertEqual(summary["metrics"]["completed_tasks"], 90)

    def test_08_role_toggle_and_sovereign_protection(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.toggle_role("EXEC-01", False)

        toggled = self.engine.toggle_role("PHY-01", True)
        self.assertTrue(toggled["is_active"])

        toggled_back = self.engine.toggle_role("PHY-01", False)
        self.assertFalse(toggled_back["is_active"])

    def test_09_api_routes_and_sovereign_approval(self) -> None:
        code, dash = dispatch_api_request(self.engine, "GET", "/api/dashboard", {}, {})
        self.assertEqual(code, 200)
        self.assertEqual(dash["metrics"]["total_roles"], 69)

        code, ap = dispatch_api_request(
            self.engine,
            "POST",
            "/api/approvals/decide",
            {},
            {"approval_id": "APR-001", "decision": "APPROVED"},
        )
        self.assertEqual(code, 200)
        self.assertEqual(ap["status"], "APPROVED")

        code, art = dispatch_api_request(
            self.engine,
            "POST",
            "/api/vault/create",
            {},
            {
                "artifact_type": "ADR",
                "project_id": "PROJ-V1-01",
                "title": "ADR-002: Companion Light & Dark Tokens",
                "content": "Verified companion appearances.",
            },
        )
        self.assertEqual(code, 201)
        self.assertEqual(art["artifact_type"], "ADR")

        code, prop = dispatch_api_request(
            self.engine,
            "POST",
            "/api/proposal/generate",
            {},
            {
                "client_name": "Apex Health",
                "client_email": "founder@apexhealth.com",
                "project_title": "Sprint Zero Medical Architecture",
                "total_cost_usd": 12500.0,
            },
        )
        self.assertEqual(code, 201)
        self.assertIn("Statement of Work", prop["proposal_markdown"])
        self.assertEqual(prop["payment_schedule"]["m1_deposit_50"], 6250)

    def test_10_ui_companion_themes_and_wcag_labels(self) -> None:
        html = Path(UI_HTML_PATH).read_text(encoding="utf-8")
        self.assertIn('[data-theme="light"]', html)
        self.assertIn('[data-theme="dark"]', html)
        self.assertIn('<label for="opp-pain">', html)
        self.assertIn('<label for="saas-clients">', html)
        self.assertIn('<label for="art-title">', html)


if __name__ == "__main__":
    unittest.main()
