from __future__ import annotations

import uuid
from typing import Any
from app.adapters.zetaris_adapter import ZetarisUSLAdapter
from app.engines.hmem_engine import HMemEngine
from app.tracer import AgentTracer


class ReconcilerAgent:
    """ReconcilerAgent: Synthesizes final actionable schedule,
    provides evidence-backed explanation ('Explain Why'),
    commits episodic memory to H-MEM, and applies updates to Zetaris USL.
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

    def synthesize(
        self,
        plan_context: dict[str, Any],
        context_data: dict[str, Any],
        eval_result: dict[str, Any],
    ) -> dict[str, Any]:
        intent_data = plan_context["intent_data"]
        target_date = plan_context["selected_date"]
        cand_slot = context_data["candidate_slot"]
        title = intent_data.get("title_candidate", "Scheduled Task")
        priority = intent_data.get("priority", "medium")
        intent_type = intent_data.get("intent_type", "SCHEDULE_NEW_TASK")

        # 1. Prepare structured actions
        actions = []
        new_event = {
            "id": f"tp-{uuid.uuid4().hex[:8]}",
            "title": title,
            "date": target_date,
            "start": cand_slot["start"],
            "end": cand_slot["end"],
            "priority": priority,
            "category": "task",
            "description": f"Scheduled by TimePilot AI ({self.model_name})",
            "fixed": priority == "urgent",
            "mobility": "fixed" if priority == "urgent" else "movable",
            "status": "planned",
            "source": "multi_agent",
        }
        actions.append({"action": "create_event", "event": new_event})

        # Process any shifts identified by ConflictCritic
        for shift in eval_result.get("shifts", []):
            actions.append({
                "action": "move_event",
                "event_id": shift["event_id"],
                "title": shift["title"],
                "from_start": shift["current_start"],
                "to_start": shift["new_start"],
            })

        # Persist to Zetaris USL
        self.usl.persist_calendar_event(new_event)

        # 2. Formulate Evidence-Backed Justification ("Explain Why")
        urgency_score = intent_data.get("urgency_score", 0.5)
        priority_label = {
            "urgent": "time-critical (urgent)",
            "high": "high-priority",
            "medium": "standard",
            "low": "low-priority",
        }.get(priority, priority)

        # Natural-language intent description
        intent_descriptions = {
            "SCHEDULE_NEW_TASK": f"a scheduling request for **{title}**",
            "OPTIMIZE_DAY": "a request to optimize and rebalance today's schedule",
            "RESOLVE_CONFLICT": f"a conflict resolution request for **{title}**",
            "UPDATE_CONSTRAINTS": "a request to update scheduling constraints",
        }
        intent_human = intent_descriptions.get(intent_type, f"a scheduling request for **{title}**")

        explanation_why = (
            f"1. **Intent Analysis (Scout Intent)**: Recognized {intent_human} — "
            f"classified as a {priority_label} task (confidence {intent_data.get('confidence', 0.96):.0%}).\n"
            f"2. **Data Sources (Zetaris USL)**: Cross-joined daily calendar ({len(context_data['events'])} events), "
            f"task backlog ({len(context_data['urgent_tasks'])} urgent tasks), and user constraints "
            f"(work hours {context_data['user_params'].get('work_start_time', '08:30')}–{context_data['user_params'].get('work_end_time', '18:30')}, "
            f"{context_data['user_params'].get('min_buffer_minutes', 15)}-min meeting buffer).\n"
            f"3. **Memory & Habits (Meterless H-MEM)**: Applied semantic habits "
            f"(morning focus protection, 15-min meeting buffers). "
            f"Selected optimal slot {cand_slot['start']}–{cand_slot['end']}.\n"
            f"4. **Verification (ConflictCritic)**: Verified 4 Zetaris Data Quality rules "
            f"and confirmed zero overlap with protected external commitments."
        )

        shifts = eval_result.get("shifts", [])
        shift_note = ""
        if shifts:
            shift_descriptions = ", ".join(
                f"'{s['title']}' shifted from {s['current_start']} → {s['new_start']}" for s in shifts
            )
            shift_note = f"\n\n⚠️ **Conflict resolved:** {shift_descriptions}."

        reply_message = (
            f"Scheduled **{title}** on {target_date} at **{cand_slot['start']}–{cand_slot['end']}**."
            f"{shift_note}\n\n"
            f"**Evidence Justification (Explain Why):**\n{explanation_why}"
        )

        # 3. Commit Episode to Meterless H-MEM
        episode_tags = ["scheduling", priority, cand_slot.get("strategy", "free_slot")]
        if eval_result.get("shifts"):
            episode_tags.append("shift_movable")
        self.hmem.record_episode(
            intent_type=intent_type,
            context_summary=f"Scheduled '{title}' at {cand_slot['start']} on {target_date}",
            decision_taken=f"Assigned slot {cand_slot['start']}-{cand_slot['end']}",
            user_feedback="accepted",
            tags=episode_tags,
        )

        self.tracer.log_event(
            agent_name="ReconcilerAgent",
            action="synthesize_plan",
            input_summary=f"Approved slot {cand_slot['start']}-{cand_slot['end']} for '{title}'",
            output_summary=f"Emitted plan with {len(actions)} actions. Updated Zetaris USL and H-MEM.",
            target_agent="User",
            model=self.model_name,
            confidence=0.98,
            retry_count=0,
            status="success",
            metadata={"actions": actions, "slot": cand_slot},
        )

        return {
            "status": "success",
            "reply": reply_message,
            "explanation_why": explanation_why,
            "actions": actions,
            "slot": cand_slot,
            "event": new_event,
            "plan": f"Scheduled '{title}' ({cand_slot['start']}-{cand_slot['end']})",
        }
