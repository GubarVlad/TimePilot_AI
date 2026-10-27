import unittest
from app.adapters.zetaris_adapter import ZetarisUSLAdapter


class TestZetarisUSL(unittest.TestCase):
    """Evaluation tests for Zetaris Unified Semantic Layer (USL).
    
    Verifies:
      1. 3+ Onboarded data sources (calendar_events, task_backlog, user_preferences).
      2. 2-3 Exploratory queries per source.
      3. Active cross-source USL queries.
      4. Data Quality rules execution and enforcement.
    """

    def setUp(self):
        # Force sample/in-memory mode for standalone reproducibility
        self.usl = ZetarisUSLAdapter(sample_mode=True)

    # 1. Source 1: Calendar Events Queries
    def test_source_1_calendar_events_by_date(self):
        rows = self.usl.query_calendar_events_by_date("2026-10-26")
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)
        self.assertIn("title", rows[0])
        self.assertIn("start_time", rows[0])

    def test_source_1_pinned_events_retrieval(self):
        rows = self.usl.query_pinned_or_protected_events()
        self.assertIsInstance(rows, list)

    def test_source_1_busy_summary(self):
        summary = self.usl.query_calendar_busy_summary("2026-10-26")
        self.assertIn("events_count", summary)
        self.assertIn("total_busy_minutes", summary)
        self.assertGreaterEqual(summary["events_count"], 1)

    # 2. Source 2: Task Backlog Queries
    def test_source_2_urgent_tasks(self):
        rows = self.usl.query_urgent_backlog_tasks()
        self.assertIsInstance(rows, list)
        self.assertGreaterEqual(len(rows), 1)
        # Verify urgent or high priority
        priorities = {r["priority"] for r in rows}
        self.assertTrue(priorities.issubset({"urgent", "high"}))

    def test_source_2_tasks_by_due_date(self):
        rows = self.usl.query_tasks_by_due_date("2026-10-28")
        self.assertIsInstance(rows, list)
        for r in rows:
            self.assertLessEqual(r["due_date"], "2026-10-28")

    def test_source_2_tasks_by_category(self):
        rows = self.usl.query_tasks_by_category("security")
        self.assertIsInstance(rows, list)
        if rows:
            self.assertEqual(rows[0]["category"], "security")

    # 3. Source 3: User Preferences Queries
    def test_source_3_user_parameters(self):
        params = self.usl.query_user_work_parameters("user_default")
        self.assertEqual(params["user_id"], "user_default")
        self.assertIn("work_start_time", params)
        self.assertIn("work_end_time", params)
        self.assertIn("min_buffer_minutes", params)

    def test_source_3_protected_categories(self):
        cats = self.usl.query_protected_categories("user_default")
        self.assertIn("medical", cats)

    # 4. Cross-Source USL Queries
    def test_usl_cross_source_schedule_with_buffers(self):
        rows = self.usl.query_unified_schedule_with_buffers("2026-10-26")
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)
        first = rows[0]
        self.assertIn("min_buffer_minutes", first)
        self.assertIn("is_immutable", first)

    def test_usl_cross_source_feasibility(self):
        report = self.usl.query_backlog_calendar_feasibility("2026-10-26")
        self.assertIsInstance(report, list)
        self.assertGreater(len(report), 0)
        self.assertIn("feasibility", report[0])
        self.assertIn(report[0]["feasibility"], ["FEASIBLE", "NEEDS_OPTIMIZATION"])

    def test_usl_find_free_focus_slots(self):
        slots = self.usl.find_free_focus_slots("2026-10-26", required_minutes=30)
        self.assertIsInstance(slots, list)

    # 5. Data Quality Rules Execution
    def test_data_quality_rules_execution(self):
        dq = self.usl.execute_data_quality_rules()
        self.assertIn("all_passed", dq)
        self.assertIn("rules_passed", dq)
        self.assertGreaterEqual(dq["rules_passed"], 1)
        self.assertEqual(dq["total_rules"], 4)


if __name__ == "__main__":
    unittest.main()

