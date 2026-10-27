from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
MEMORY_FILE = DATA_DIR / "hmem_store.json"


class WorkingMemory:
    """Tier 1: Fast in-turn working memory buffer."""

    def __init__(self):
        self.active_goal: str = ""
        self.selected_date: str = ""
        self.extracted_entities: dict[str, Any] = {}
        self.candidate_slots: list[dict[str, Any]] = []
        self.critic_feedback: list[str] = []
        self.unresolved_conflicts: list[dict[str, Any]] = []

    def set_goal(self, goal: str, selected_date: str) -> None:
        self.active_goal = goal
        self.selected_date = selected_date

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_goal": self.active_goal,
            "selected_date": self.selected_date,
            "extracted_entities": self.extracted_entities,
            "candidate_slots": self.candidate_slots,
            "critic_feedback": self.critic_feedback,
            "unresolved_conflicts": self.unresolved_conflicts,
        }

    def reset(self) -> None:
        self.active_goal = ""
        self.selected_date = ""
        self.extracted_entities.clear()
        self.candidate_slots.clear()
        self.critic_feedback.clear()
        self.unresolved_conflicts.clear()


class EpisodicMemoryRecord:
    """Tier 2: Single episodic record of an interaction or decision."""

    def __init__(
        self,
        episode_id: str,
        timestamp: str,
        intent_type: str,
        context_summary: str,
        decision_taken: str,
        user_feedback: str = "accepted",
        tags: Optional[list[str]] = None,
    ):
        self.episode_id = episode_id
        self.timestamp = timestamp
        self.intent_type = intent_type
        self.context_summary = context_summary
        self.decision_taken = decision_taken
        self.user_feedback = user_feedback
        self.tags = tags or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "timestamp": self.timestamp,
            "intent_type": self.intent_type,
            "context_summary": self.context_summary,
            "decision_taken": self.decision_taken,
            "user_feedback": self.user_feedback,
            "tags": self.tags,
        }


class SemanticHabit:
    """Tier 3: Long-term generalized semantic belief/habit."""

    def __init__(
        self,
        habit_key: str,
        description: str,
        confidence: float,
        evidence_count: int,
        preferred_value: Any,
    ):
        self.habit_key = habit_key
        self.description = description
        self.confidence = confidence
        self.evidence_count = evidence_count
        self.preferred_value = preferred_value

    def to_dict(self) -> dict[str, Any]:
        return {
            "habit_key": self.habit_key,
            "description": self.description,
            "confidence": round(self.confidence, 2),
            "evidence_count": self.evidence_count,
            "preferred_value": self.preferred_value,
        }


class HMemEngine:
    """Meterless H-MEM Engine (Hierarchical Memory Architecture).
    
    Provides 3-tier memory retention, consolidation, and retrieval:
      - Tier 1: Working Memory (active context)
      - Tier 2: Episodic Memory (discrete past decisions)
      - Tier 3: Semantic Long-Term Memory (generalized user habits)
    """

    def __init__(self, persistence_file: Optional[Path] = None):
        self.persistence_file = persistence_file or MEMORY_FILE
        self.working_memory = WorkingMemory()
        self.episodic_memory: list[EpisodicMemoryRecord] = []
        self.semantic_habits: dict[str, SemanticHabit] = {}
        self._init_defaults()
        self.load()

    def _init_defaults(self) -> None:
        """Seed initial baseline semantic habits."""
        self.semantic_habits = {
            "morning_focus_bias": SemanticHabit(
                habit_key="morning_focus_bias",
                description="Prefers deep work and strategic planning before 12:00",
                confidence=0.88,
                evidence_count=12,
                preferred_value={"window": "09:00-12:00", "weight": 1.5},
            ),
            "meeting_buffer_affinity": SemanticHabit(
                habit_key="meeting_buffer_affinity",
                description="Enforces 15-minute breathing room after client or team meetings",
                confidence=0.92,
                evidence_count=19,
                preferred_value={"buffer_minutes": 15, "strict": True},
            ),
            "protected_lunch_window": SemanticHabit(
                habit_key="protected_lunch_window",
                description="Disallows scheduling tasks during lunch hour (12:30-13:30)",
                confidence=0.95,
                evidence_count=24,
                preferred_value={"start": "12:30", "end": "13:30"},
            ),
            "flexible_task_shift_preference": SemanticHabit(
                habit_key="flexible_task_shift_preference",
                description="When high priority items arrive, prefer shifting movable tasks over declining",
                confidence=0.84,
                evidence_count=8,
                preferred_value={"shift_strategy": "forward_slot"},
            ),
        }

    def load(self) -> None:
        """Load episodic and semantic state from storage."""
        if not self.persistence_file.exists():
            return
        try:
            data = json.loads(self.persistence_file.read_text(encoding="utf-8"))
            # Load episodic
            self.episodic_memory = [
                EpisodicMemoryRecord(**item) for item in data.get("episodic_memory", [])
            ]
            # Load semantic
            for k, val in data.get("semantic_habits", {}).items():
                self.semantic_habits[k] = SemanticHabit(**val)
        except Exception as exc:
            print(f"[HMemEngine] Warning loading memory: {exc}")

    def save(self) -> None:
        """Persist memory state."""
        try:
            data = {
                "version": 1,
                "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "episodic_memory": [e.to_dict() for e in self.episodic_memory[-50:]],
                "semantic_habits": {k: h.to_dict() for k, h in self.semantic_habits.items()},
            }
            self.persistence_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as exc:
            print(f"[HMemEngine] Error persisting memory: {exc}")

    # =========================================================================
    # TIER 1: WORKING MEMORY OPERATIONS
    # =========================================================================
    def start_turn(self, goal: str, selected_date: str) -> None:
        self.working_memory.reset()
        self.working_memory.set_goal(goal, selected_date)

    def update_working_slots(self, candidate_slots: list[dict[str, Any]]) -> None:
        self.working_memory.candidate_slots = candidate_slots

    def record_critic_critique(self, feedback: str) -> None:
        self.working_memory.critic_feedback.append(feedback)

    # =========================================================================
    # TIER 2: EPISODIC MEMORY OPERATIONS
    # =========================================================================
    def record_episode(
        self,
        intent_type: str,
        context_summary: str,
        decision_taken: str,
        user_feedback: str = "accepted",
        tags: Optional[list[str]] = None,
    ) -> EpisodicMemoryRecord:
        """Store a new episode and trigger consolidation into semantic habits."""
        episode = EpisodicMemoryRecord(
            episode_id=f"ep_{len(self.episodic_memory) + 1}_{int(dt.datetime.now().timestamp())}",
            timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
            intent_type=intent_type,
            context_summary=context_summary,
            decision_taken=decision_taken,
            user_feedback=user_feedback,
            tags=tags or [],
        )
        self.episodic_memory.append(episode)
        self._consolidate_episode(episode)
        self.save()
        return episode

    def recall_relevant_episodes(self, query_tags: list[str], limit: int = 3) -> list[dict[str, Any]]:
        """Retrieve relevant past episodes using tag overlap and recency weighting."""
        scored: list[tuple[float, EpisodicMemoryRecord]] = []
        now = dt.datetime.now(dt.timezone.utc)

        for ep in self.episodic_memory:
            overlap = len(set(query_tags).intersection(set(ep.tags)))
            try:
                ep_time = dt.datetime.fromisoformat(ep.timestamp.replace("Z", "+00:00"))
                days_ago = max(0.1, (now - ep_time).total_seconds() / 86400.0)
            except Exception:
                days_ago = 1.0

            recency_weight = math.exp(-0.05 * days_ago)
            score = (overlap * 1.5 + (1.0 if ep.user_feedback == "accepted" else 0.2)) * recency_weight
            if score > 0.1:
                scored.append((score, ep))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep.to_dict() for _, ep in scored[:limit]]

    # =========================================================================
    # TIER 3: SEMANTIC CONSOLIDATION & RETRIEVAL
    # =========================================================================
    def _consolidate_episode(self, episode: EpisodicMemoryRecord) -> None:
        """Consolidate episodic observation into generalized semantic habits."""
        if "shift_movable" in episode.tags and episode.user_feedback == "accepted":
            habit = self.semantic_habits.get("flexible_task_shift_preference")
            if habit:
                habit.confidence = min(0.99, habit.confidence + 0.02)
                habit.evidence_count += 1

        if "morning_focus" in episode.tags and episode.user_feedback == "accepted":
            habit = self.semantic_habits.get("morning_focus_bias")
            if habit:
                habit.confidence = min(0.99, habit.confidence + 0.01)
                habit.evidence_count += 1

        if "buffer" in episode.tags and episode.user_feedback == "accepted":
            habit = self.semantic_habits.get("meeting_buffer_affinity")
            if habit:
                habit.confidence = min(0.99, habit.confidence + 0.01)
                habit.evidence_count += 1

    def get_semantic_context(self) -> dict[str, Any]:
        """Return the active semantic habits formatted for agent prompt & reasoning."""
        return {
            k: {
                "description": h.description,
                "confidence": h.confidence,
                "preferred_value": h.preferred_value,
            }
            for k, h in self.semantic_habits.items()
        }

