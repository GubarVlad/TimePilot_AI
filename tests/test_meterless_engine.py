import unittest
import tempfile
from pathlib import Path
from app.engines.hmem_engine import HMemEngine, WorkingMemory, EpisodicMemoryRecord, SemanticHabit
from app.engines.scout_intent_engine import ScoutIntentEngine


class TestMeterlessEngines(unittest.TestCase):
    """Conformance tests for Meterless Engines: H-MEM and Scout Intent."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_file = Path(self.tmp_dir.name) / "test_hmem.json"
        self.hmem = HMemEngine(persistence_file=self.tmp_file)
        self.scout = ScoutIntentEngine()

    def tearDown(self):
        self.tmp_dir.cleanup()

    # --- H-MEM Engine Tests ---
    def test_hmem_working_memory_lifecycle(self):
        wm = self.hmem.working_memory
        wm.set_goal("Plan Q4 Roadmap", "2026-10-27")
        wm.candidate_slots = [{"start": "10:00", "end": "11:00"}]
        wm.record_critic_critique = ["Collision at 10:00"]
        
        state = wm.to_dict()
        self.assertEqual(state["active_goal"], "Plan Q4 Roadmap")
        self.assertEqual(state["selected_date"], "2026-10-27")
        self.assertEqual(len(state["candidate_slots"]), 1)
        
        wm.reset()
        self.assertEqual(wm.active_goal, "")
        self.assertEqual(len(wm.candidate_slots), 0)

    def test_hmem_episodic_recording_and_recall(self):
        # Record episodes
        ep1 = self.hmem.record_episode(
            intent_type="SCHEDULE_NEW_TASK",
            context_summary="Scheduled urgent bugfix",
            decision_taken="Assigned 14:00 slot",
            user_feedback="accepted",
            tags=["urgent", "bugfix", "shift_movable"],
        )
        self.assertIsNotNone(ep1.episode_id)

        # Recall with matching tags
        recalled = self.hmem.recall_relevant_episodes(["urgent", "bugfix"], limit=2)
        self.assertGreaterEqual(len(recalled), 1)
        self.assertEqual(recalled[0]["intent_type"], "SCHEDULE_NEW_TASK")
        self.assertIn("urgent", recalled[0]["tags"])

    def test_hmem_semantic_consolidation_and_habit_reinforcement(self):
        initial_conf = self.hmem.semantic_habits["flexible_task_shift_preference"].confidence
        # Consolidate an accepted shift episode
        self.hmem.record_episode(
            intent_type="RESOLVE_CONFLICT",
            context_summary="Shifted flexible sync to accommodate urgent client meeting",
            decision_taken="Moved 30 min later",
            user_feedback="accepted",
            tags=["shift_movable", "conflict"],
        )
        new_conf = self.hmem.semantic_habits["flexible_task_shift_preference"].confidence
        self.assertGreater(new_conf, initial_conf)

        semantic_context = self.hmem.get_semantic_context()
        self.assertIn("morning_focus_bias", semantic_context)
        self.assertIn("meeting_buffer_affinity", semantic_context)

    # --- Scout Intent Engine Tests ---
    def test_scout_intent_classification_urgent_task(self):
        msg = "Срочно добавь подготовку отчёта завтра в 14:00 на полтора часа, критично!"
        result = self.scout.analyze(msg, "2026-10-27")
        
        self.assertEqual(result["intent_type"], "SCHEDULE_NEW_TASK")
        self.assertEqual(result["priority"], "urgent")
        self.assertGreaterEqual(result["urgency_score"], 0.9)
        self.assertEqual(result["duration_minutes"], 90)
        self.assertEqual(result["time_hint"], "14:00")
        self.assertFalse(result["requires_clarification"])

    def test_scout_intent_explain_why(self):
        msg = "Почему ты перенес встречу с дизайнером на 16:30?"
        result = self.scout.analyze(msg, "2026-10-27")
        self.assertEqual(result["intent_type"], "EXPLAIN_WHY")
        self.assertGreaterEqual(result["confidence"], 0.9)

    def test_scout_intent_free_time_query(self):
        msg = "Когда сегодня есть свободное окно на 45 минут?"
        result = self.scout.analyze(msg, "2026-10-27")
        self.assertEqual(result["intent_type"], "QUERY_FREE_TIME")
        self.assertEqual(result["duration_minutes"], 45)


if __name__ == "__main__":
    unittest.main()

