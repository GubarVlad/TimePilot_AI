from __future__ import annotations

from typing import Any, Optional
from app.adapters.zetaris_adapter import ZetarisUSLAdapter
from app.engines.hmem_engine import HMemEngine
from app.tracer import AgentTracer


class ContextAgent:
    """ContextAgent: Connects to Zetaris Unified Semantic Layer (USL)
    and Meterless H-MEM hierarchical memory to ground the plan in reality.
    """

    def __init__(
        self,
        zetaris_usl: ZetarisUSLAdapter,
        hmem_engine: HMemEngine,
        tracer: AgentTracer,
        model_name: str = "nvidia/nemotron-3-super-120b-a12b",
    ):
        self.usl = zetaris_usl
        self.hmem = hmem_engine
        self.tracer = tracer
        self.model_name = model_name

    def retrieve_and_propose(
        self,
        plan_context: dict[str, Any],
        critic_feedback: Optional[str] = None,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        intent_data = plan_context["intent_data"]
        target_date = plan_context["selected_date"]
        dur = intent_data.get("duration_minutes", 60)
        time_hint = intent_data.get("time_hint")

        # 1. Query Zetaris USL
        events = self.usl.query_unified_schedule_with_buffers(target_date)
        user_params = self.usl.query_user_work_parameters()
        urgent_tasks = self.usl.query_urgent_backlog_tasks()

        # 2. Query Meterless H-MEM
        tags = ["scheduling", intent_data.get("priority", "medium")]
        if "срочн" in intent_data.get("raw_message", "").lower():
            tags.append("urgent")
        past_episodes = self.hmem.recall_relevant_episodes(tags, limit=2)
        semantic_habits = self.hmem.get_semantic_context()

        # 3. Propose candidate slot
        candidate_slot = None
        
        # If there's critique feedback requiring revision:
        if critic_feedback and "after" in critic_feedback:
            # Adjust based on critic recommendation
            import re
            m = re.search(r"after\s+(\d{1,2}:\d{2})", critic_feedback)
            if m:
                adjusted_start = m.group(1)
                sh, sm = [int(p) for p in adjusted_start.split(":")]
                end_m = sh * 60 + sm + dur
                candidate_slot = {
                    "start": adjusted_start,
                    "end": f"{end_m // 60:02d}:{end_m % 60:02d}",
                    "date": target_date,
                    "strategy": "critic_adjusted_slot",
                }
        elif time_hint:
            sh, sm = [int(p) for p in time_hint.split(":")]
            end_m = sh * 60 + sm + dur
            candidate_slot = {
                "start": time_hint,
                "end": f"{end_m // 60:02d}:{end_m % 60:02d}",
                "date": target_date,
                "strategy": "explicit_user_hint",
            }
        else:
            free_slots = self.usl.find_free_focus_slots(target_date, dur)
            if free_slots:
                # Pick slot aligned with habits (morning focus preferred)
                morning_bias = semantic_habits.get("morning_focus_bias", {}).get("confidence", 0.5) > 0.7
                chosen = free_slots[0]
                if morning_bias:
                    for s in free_slots:
                        if s["start"] >= "09:00" and s["start"] <= "11:30":
                            chosen = s
                            break
                candidate_slot = {
                    "start": chosen["start"],
                    "end": chosen["end"],
                    "date": target_date,
                    "strategy": "hmem_habit_aligned_free_slot",
                }
            else:
                candidate_slot = {
                    "start": "16:00",
                    "end": f"{(16*60 + dur) // 60:02d}:{(16*60 + dur) % 60:02d}",
                    "date": target_date,
                    "strategy": "fallback_afternoon",
                }

        output_summary = (
            f"Zetaris returned {len(events)} events, {len(urgent_tasks)} backlog items. "
            f"H-MEM recalled {len(past_episodes)} episodes. Proposing slot {candidate_slot['start']}-{candidate_slot['end']}."
        )

        self.tracer.log_event(
            agent_name="ContextAgent",
            action="provide_context",
            input_summary=f"Retrieval for date={target_date}, dur={dur}m (retry={retry_count})",
            output_summary=output_summary,
            target_agent="ConflictCritic",
            model=self.model_name,
            confidence=0.91,
            retry_count=retry_count,
            status="success",
            metadata={
                "candidate_slot": candidate_slot,
                "events_count": len(events),
                "urgent_tasks_count": len(urgent_tasks),
            },
        )

        return {
            "events": events,
            "urgent_tasks": urgent_tasks,
            "user_params": user_params,
            "candidate_slot": candidate_slot,
            "past_episodes": past_episodes,
            "semantic_habits": semantic_habits,
        }

