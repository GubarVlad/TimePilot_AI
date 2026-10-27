from __future__ import annotations

from typing import Any
from app.engines.scout_intent_engine import ScoutIntentEngine
from app.tracer import AgentTracer


class PlannerAgent:
    """PlannerAgent: Decomposes user goal, runs intent discovery,
    and orchestrates execution trajectory.
    """

    def __init__(self, tracer: AgentTracer, model_name: str = "nvidia/nemotron-3-super-120b-a12b"):
        self.tracer = tracer
        self.model_name = model_name
        self.intent_engine = ScoutIntentEngine()

    def plan(self, message: str, selected_date: str) -> dict[str, Any]:
        # 1. Scout Intent Analysis
        intent_data = self.intent_engine.analyze(message, selected_date)
        
        input_summary = f"User request: '{message[:80]}...' on date {selected_date}"
        output_summary = (
            f"Classified intent: {intent_data['intent_type']} (conf: {intent_data['confidence']:.2f}, "
            f"urgency: {intent_data['urgency_score']:.2f}, slot_dur: {intent_data['duration_minutes']}m)"
        )
        
        self.tracer.log_event(
            agent_name="PlannerAgent",
            action="delegate",
            input_summary=input_summary,
            output_summary=f"Delegated context retrieval to ContextAgent. {output_summary}",
            target_agent="ContextAgent",
            model=self.model_name,
            confidence=intent_data["confidence"],
            retry_count=0,
            status="success",
            metadata={"intent_data": intent_data},
        )

        return {
            "intent_data": intent_data,
            "selected_date": selected_date,
            "raw_message": message,
        }

