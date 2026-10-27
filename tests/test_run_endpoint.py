import io
import json
import unittest
from pathlib import Path
from run import run_cli
from app.agents.orchestrator import MultiAgentOrchestrator


class TestRunEndpointAndCLI(unittest.TestCase):
    """Verifies that the agent can be programmatically driven as required by the judges."""

    def test_cli_execution_with_sample_1(self):
        code = run_cli("input_examples/example_1.json")
        self.assertEqual(code, 0)

    def test_cli_execution_with_sample_2(self):
        code = run_cli("input_examples/example_2.json")
        self.assertEqual(code, 0)

    def test_cli_execution_with_sample_3(self):
        code = run_cli("input_examples/example_3.json")
        self.assertEqual(code, 0)

    def test_orchestrator_structured_contract(self):
        orchestrator = MultiAgentOrchestrator()
        result = orchestrator.process_request(
            user_message="Срочно запланируй созвон с ментором завтра в 11:30 на 30 минут",
            selected_date="2026-10-27",
        )
        # Contract checks
        self.assertEqual(result["status"], "success")
        self.assertIn("plan", result)
        self.assertIn("explanation_why", result)
        self.assertIn("actions", result)
        self.assertIn("traces", result)
        self.assertIn("zetaris_usl", result)
        self.assertIn("meterless_engine", result)
        self.assertIn("ai_provider", result)

        # Traces check
        self.assertGreaterEqual(result["traces_count"], 3)
        self.assertEqual(result["meterless_engine"]["engine"], "H-MEM + Scout Intent")
        self.assertIn("src_calendar_events", result["zetaris_usl"]["sources_queried"])


if __name__ == "__main__":
    unittest.main()

