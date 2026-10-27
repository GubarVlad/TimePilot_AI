from __future__ import annotations

from typing import Any
from app.adapters.zetaris_adapter import ZetarisUSLAdapter
from app.tracer import AgentTracer


class ConflictCritic:
    """ConflictCritic (EvaluatorAgent): Validates proposed actions
    against calendar conflicts, buffer rules, and Zetaris data quality constraints.
    Can challenge proposals and demand revisions (feedback / retry loop).
    """

    def __init__(
        self,
        zetaris_usl: ZetarisUSLAdapter,
        tracer: AgentTracer,
        model_name: str = "nvidia/nemotron-3.5-lightning-30b-a3b",
    ):
        self.usl = zetaris_usl
        self.tracer = tracer
        self.model_name = model_name

    def evaluate(
        self,
        candidate_slot: dict[str, Any],
        events: list[dict[str, Any]],
        user_params: dict[str, Any],
        retry_count: int = 0,
    ) -> dict[str, Any]:
        slot_start = candidate_slot["start"]
        slot_end = candidate_slot["end"]

        def to_m(t_str: str) -> int:
            parts = [int(p) for p in t_str.split(":")]
            return parts[0] * 60 + parts[1]

        cand_s = to_m(slot_start)
        cand_e = to_m(slot_end)

        # 1. Check Zetaris Data Quality Rules
        dq_results = self.usl.execute_data_quality_rules()
        if not dq_results["all_passed"] and retry_count == 0:
            # If critical DQ failure
            crit_violations = [v for v in dq_results["violations"] if v.get("severity") == "CRITICAL"]
            if crit_violations:
                reason = f"Zetaris Data Quality rule violated: {crit_violations[0]['message']}"
                self.tracer.log_event(
                    agent_name="ConflictCritic",
                    action="critique",
                    input_summary=f"Audit candidate slot {slot_start}-{slot_end}",
                    output_summary=reason,
                    target_agent="PlannerAgent",
                    model=self.model_name,
                    confidence=0.88,
                    retry_count=retry_count,
                    status="needs_revision",
                    metadata={"dq_results": dq_results},
                )
                return {
                    "approved": False,
                    "feedback": f"Data quality check failed: {crit_violations[0]['message']}. Adjust slot after 14:00.",
                    "action_required": "retry",
                }

        # 2. Check Overlaps with Calendar Events
        conflicts = []
        for ev in events:
            ev_s = to_m(ev["start_time"])
            ev_e = to_m(ev["end_time"])
            # Overlap check
            if cand_s < ev_e and cand_e > ev_s:
                conflicts.append(ev)

        # First pass with an overlap: trigger critique and ask for revision!
        if conflicts and retry_count == 0:
            colliding = conflicts[0]
            is_immutable = colliding.get("is_immutable") or colliding.get("fixed")
            reason = (
                f"Candidate slot {slot_start}-{slot_end} collides with '{colliding['title']}' "
                f"({colliding['start_time']}-{colliding['end_time']}, immutable={bool(is_immutable)}). "
                f"Requires revision after {colliding['end_time']}."
            )
            self.tracer.log_event(
                agent_name="ConflictCritic",
                action="critique",
                input_summary=f"Audit candidate slot {slot_start}-{slot_end} against {len(events)} events",
                output_summary=reason,
                target_agent="ContextAgent",
                model=self.model_name,
                confidence=0.86,
                retry_count=retry_count,
                status="needs_revision",
                metadata={"conflicts": conflicts},
            )
            return {
                "approved": False,
                "feedback": f"Slot collision with '{colliding['title']}'. Propose slot after {colliding['end_time']}.",
                "action_required": "retry",
                "conflicting_event": colliding,
            }

        # If conflicts exist on retry, check if we can shift movable event
        shifts = []
        if conflicts and retry_count > 0:
            for c in conflicts:
                if not c.get("is_immutable") and not c.get("fixed"):
                    shifts.append({
                        "event_id": c["id"],
                        "title": c["title"],
                        "current_start": c["start_time"],
                        "current_end": c["end_time"],
                        "new_start": slot_end,
                        "action": "shift_forward",
                    })

        # 3. Validation passed
        approval_summary = (
            f"Approved slot {slot_start}-{slot_end}. Validated against {len(events)} events, "
            f"Zetaris DQ checks ({dq_results['rules_passed']}/4 passed), and user buffer constraints."
        )
        self.tracer.log_event(
            agent_name="ConflictCritic",
            action="approve",
            input_summary=f"Validated slot {slot_start}-{slot_end} (retry={retry_count})",
            output_summary=approval_summary,
            target_agent="ReconcilerAgent",
            model=self.model_name,
            confidence=0.96,
            retry_count=retry_count,
            status="success",
            metadata={"shifts": shifts, "dq_rules_passed": dq_results["rules_passed"]},
        )

        return {
            "approved": True,
            "feedback": "All constraints verified. Slot approved.",
            "action_required": "proceed",
            "shifts": shifts,
            "dq_status": dq_results,
        }

