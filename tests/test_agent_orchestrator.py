import unittest
from app.agents.orchestrator import MultiAgentOrchestrator
from app.adapters.zetaris_adapter import ZetarisUSLAdapter
from app.engines.hmem_engine import HMemEngine
from app.tracer import AgentTracer


class TestMultiAgentOrchestrator(unittest.TestCase):
    """Verifies collaborative multi-agent loop, handoffs, critique, and traces."""

    def setUp(self):
        self.tracer = AgentTracer(echo_stdout=False)
        self.usl = ZetarisUSLAdapter(sample_mode=True)
        self.hmem = HMemEngine()
        self.orchestrator = MultiAgentOrchestrator(
            zetaris_usl=self.usl,
            hmem_engine=self.hmem,
            tracer=self.tracer,
        )

    def test_full_multi_agent_planning_loop(self):
        msg = "Срочно запланируй код-ревью безопасности завтра в 14:00 на 45 минут"
        result = self.orchestrator.process_request(msg, selected_date="2026-10-27")

        self.assertEqual(result["status"], "success")
        self.assertIn("reply", result)
        self.assertIn("explanation_why", result)
        self.assertGreater(len(result["actions"]), 0)
        
        # Verify Zetaris USL metadata
        self.assertIn("zetaris_usl", result)
        self.assertGreaterEqual(result["zetaris_usl"]["data_quality_rules_passed"], 1)
        self.assertIn("src_calendar_events", result["zetaris_usl"]["sources_queried"])
        
        # Verify Meterless metadata
        self.assertIn("meterless_engine", result)
        self.assertEqual(result["meterless_engine"]["engine"], "H-MEM + Scout Intent")
        self.assertTrue(result["meterless_engine"]["working_memory_active"])

        # Verify Traces
        traces = result["traces"]
        self.assertGreaterEqual(len(traces), 3)

        agent_names = {t["agent_name"] for t in traces}
        # Hackathon rule: At least two named agents doing distinct things
        self.assertGreaterEqual(len(agent_names), 2)
        self.assertIn("PlannerAgent", agent_names)
        self.assertIn("ContextAgent", agent_names)
        self.assertIn("ConflictCritic", agent_names)
        self.assertIn("ReconcilerAgent", agent_names)

        # Check models recorded
        models = [t["model"] for t in traces]
        self.assertTrue(any("nemotron" in m.lower() for m in models))

    def test_clarification_on_ambiguous_request(self):
        # High ambiguity message
        msg = "а"
        result = self.orchestrator.process_request(msg, selected_date="2026-10-27")
        self.assertEqual(result["status"], "clarification_needed")
        self.assertTrue("details" in result["reply"].lower() or "уточни" in result["reply"].lower())


if __name__ == "__main__":
    unittest.main()

