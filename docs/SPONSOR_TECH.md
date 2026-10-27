# Sponsor Technology Explanation

**Open Agent Hackathon 2026 | Build an agent that does real work**  
**Project:** TimePilot AI  
**Track:** Track 02 (The Agent That Can Explain Why) / Track 03 (Reasoning Architecture) / Bonus Tinkerer  

---

## 1. Zetaris (Unified Semantic Layer Data Layer)
- **Role:** Zetaris serves as the foundation data layer for TimePilot AI.
- **Integration:** TimePilot connects via `ZetarisUSLAdapter` (`app/adapters/zetaris_adapter.py`) targeting the Zetaris REST API (`ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, `ZETARIS_API_KEY`).
- **Unified Semantic Layer (USL):** Eliminates fragmented data silos by unifying:
  1. `src_calendar_events`: Current daily events, durations, and pinned state.
  2. `src_task_backlog`: Unscheduled issues from Jira/Linear, priority levels, estimated durations, and due dates.
  3. `src_user_preferences`: Working hours, buffer intervals (15 min), and protected categories (medical/flights).
- **Active Cross-Source Queries:**
  - `usl_unified_schedule`: Injects buffer rules and dynamic immutability flags.
  - `usl_cross_source_feasibility`: Computes backlog task feasibility against remaining calendar capacity.
  - `find_free_focus_slots`: Detects focus windows without violating meeting buffers.
- **Data Quality:** Automatically runs 4 Data Quality Rules (`RULE_TIME_ORDER`, `RULE_NO_OVERLAPPING_PINNED`, `RULE_VALID_PRIORITY`, `RULE_NON_EMPTY_IDENTIFIERS`) before any schedule modification is committed.
- **Sample Mode Fallback:** Full in-memory SQL execution over `data/zetaris_usl_ddl.sql` when running in offline `SAMPLE_MODE=true`.

---

## 2. Meterless (Engines & Nightshift AI Provider)
TimePilot AI implements **two Meterless Engines** and uses **Meterless Nightshift** as its primary AI provider:

### 2.1 Meterless H-MEM Engine (Hierarchical Memory Architecture)
- **Engine Location:** `app/engines/hmem_engine.py`
- **What it does:** Provides 3-tier memory retention:
  - **Tier 1 (Working Memory):** Maintains active goal, candidate time slots, and critic feedback in the active session.
  - **Tier 2 (Episodic Memory):** Records past scheduling interactions, accepted shifts, and conflict resolutions with recency decay weighting.
  - **Tier 3 (Semantic Long-Term Memory):** Consolidates episodic evidence into persistent user habits (`morning_focus_bias`, `meeting_buffer_affinity`, `protected_lunch_window`, `flexible_task_shift_preference`).
- **Feature Powered:** Context-aware scheduling that remembers user habits without re-prompting. When an urgent task arrives, H-MEM checks past decisions to shift flexible tasks rather than rejecting.
- **Passing Test:** `tests/test_meterless_engine.py` (conformance tests for WM lifecycle, episodic recall, and semantic habit consolidation).

### 2.2 Meterless Scout Intent Engine
- **Engine Location:** `app/engines/scout_intent_engine.py`
- **What it does:** Extracts multi-dimensional intent (`SCHEDULE_NEW_TASK`, `RESOLVE_CONFLICT`, `OPTIMIZE_DAY`, `EXPLAIN_WHY`, `QUERY_FREE_TIME`), computes urgency scores (0.0–1.0), extracts duration and time slots, and calculates ambiguity scores.
- **Passing Test:** `tests/test_meterless_engine.py`.

### 2.3 Meterless Nightshift Integration
- **Integration Location:** `app/adapters/nightshift_adapter.py`
- **Connection:** Targets `METERLESS_BASE_URL` (`http://127.0.0.1:8088/v1/chat/completions`) using `METERLESS_RUNTIME_TOKEN`.
- **Primary Model:** `METERLESS_MODEL=nvidia/nemotron-3-super-120b-a12b`.
- **Evaluation Model:** `EVAL_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b` used by `ConflictCritic`.

---

## 3. NVIDIA Technology (Nemotron Models & Riva ASR)
NVIDIA cloud technologies power the reasoning, evaluation, and speech interfaces:
1. **NVIDIA Nemotron via Nightshift:**
   - **`nvidia/nemotron-3-super-120b-a12b`:** Drives the `PlannerAgent`, `ContextAgent`, and `ReconcilerAgent` for deep reasoning, slot synthesis, and evidence generation.
   - **`nvidia/nemotron-3.5-lightning-30b-a3b`:** Powers the `ConflictCritic` evaluator for low-latency constraint checking, conflict detection, and quality validation.
   - **Trace Logging:** Every event in `logs/agent_traces.jsonl` explicitly records the NVIDIA model that handled the step.
2. **NVIDIA Riva / Parakeet Multilingual ASR:**
   - Streaming multilingual speech-to-text (`Parakeet-RNNT 1.1B Multilingual`) over gRPC (`grpc.nvcf.nvidia.com:443`). Enables hands-free voice scheduling directly in Russian and English from the web interface.

---

## 4. Cursor (with Space XAI)
- **Role:** Cursor was used as the primary AI-accelerated IDE throughout the hackathon build window.
- **Workflow:** Used Cursor's multi-file editing to architect the multi-agent system (`app/agents/`), scaffold the Zetaris adapter with SQL schema validation, and generate end-to-end tests for the Meterless H-MEM engine.

---

## 5. What Was Unique About Our Use of Sponsor Technologies
1. **Closed-Loop Critique & Self-Correction:** Instead of a simple prompt wrapper or linear pipeline, TimePilot AI implements a collaborative 4-agent loop: `PlannerAgent` → `ContextAgent` (querying Zetaris USL & H-MEM) → `ConflictCritic` (evaluating Zetaris Data Quality rules). When `ConflictCritic` detects an overlap, it **rejects the proposal, flags the specific conflict, and demands a revision (`retry_count += 1`)**, guiding the agent to find an optimal alternate slot and shift movable tasks.
2. **Unified Semantic Feasibility Modeling:** Rather than checking calendar conflicts purely in Python code, TimePilot delegates complex cross-source reasoning (comparing backlog task estimates against daily free capacity minus meeting buffers) to **Zetaris USL SQL views (`usl_cross_source_feasibility`)**.
3. **Consolidation of Episodic Memory into Behavioral Habits:** Meterless H-MEM doesn't just store chat logs; it consolidates accepted schedule adjustments into reinforced confidence scores for long-term semantic habits (`flexible_task_shift_preference`, `morning_focus_bias`), creating an agent that genuinely learns and adapts to user work patterns over time.
4. **Verifiable Explain Why:** For every schedule adjustment, the ReconcilerAgent outputs a structured breakdown detailing the exact Zetaris queries, H-MEM memory entries, and ConflictCritic constraints that led to the decision.

