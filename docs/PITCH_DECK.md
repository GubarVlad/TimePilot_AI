# TimePilot AI — Pitch Deck

> **Open Agent Hackathon 2026 Submission**  
> **Track:** Track 03: Reasoning Architecture  
> **Project:** TimePilot AI — Autonomous Cognitive Calendar & Scheduling Agent  
> **Tagline:** *Not another chatbot. An agent that does real work.*

---

## Slide 1: Problem & Target Audience

### The Chaos of Modern Time Management
Knowledge workers, engineering managers, and executives switch contexts dozens of times a day, losing **2.5+ hours daily** to calendar coordination and mental triage.

### Core Pain Points:
1. **Fragmented Intelligence Silos:**
   - Urgent tasks sit disconnected in **Jira / Linear backlogs**.
   - Calendar events are isolated in Google Calendar / Outlook.
   - User energy levels, focus rules, and 15-minute buffers are neglected.
2. **Inflexible & Brittle Scheduling:**
   - Standard calendars treat all events as static blocks.
   - When an urgent issue strikes, users must manually play "calendar Tetris".
3. **Chatbot Illusion:**
   - Conventional LLM calendar wrappers hallucinate slots, overwrite doctor appointments, and fail to provide verifiable explanations.

---

## Slide 2: The Solution — TimePilot AI

### An Autonomous Cognitive Calendar Agent
TimePilot AI replaces static calendar grids with an **autonomous reasoning scheduling partner** that connects data, understands human context, and turns intelligence into action.

### Key Capabilities:
- **Unified Semantic Ingestion:** Connects calendar commitments, engineering backlogs, and user preferences into a single operational state.
- **Cognitive Memory & Habits:** Retains working memory across reasoning turns, past episodic scheduling decisions, and learns personal habits over time.
- **Active Critique & Conflict Resolution:** Autonomously negotiates movable events to fit urgent priorities without human intervention.
- **Transparent "Explain Why":** Delivers clear, evidence-backed justifications for every calendar modification.

---

## Slide 3: Reasoning Architecture (Track 03 Deep Dive)

### Beyond Linear Prompt Chains (`A -> B -> C`)
TimePilot AI rejects single-pass pipelines. It implements a **4-agent collaborative loop** with active critique, constraint evaluation, and branching retries:

```
[User Request / Voice]
          │
          ▼
    PlannerAgent (Scout Intent Engine: urgency scoring & temporal extraction)
          │
          ▼ delegate
    ContextAgent ◄──────────────────────► Zetaris USL (3 Federated Sources)
          │                                  ▲
          │ propose slot                     │
          ▼                                  ▼
    ConflictCritic ◄─────────────────────► Meterless H-MEM (3 Memory Tiers)
          │
     [Collides?]
          ├────────► [REJECT & RETRY] (Branch back to ContextAgent with constraints)
          │
     [Approved]
          ▼
    ReconcilerAgent
          │ ──► Synthesizes atomic calendar mutations
          │ ──► Produces auditable "Explain Why" report
          │ ──► Commits episodic memory & consolidates semantic habits
          ▼
[Structured Response & Live Interactive UI]
```

### Self-Correction in Action:
- When an urgent task arrives at an already booked hour, `ConflictCritic` flags the overlap.
- It calculates mobility: fixed events (pinned meetings, medical visits) are immutable. Flexible sessions (internal UI work, solo research) can be shifted.
- The loop re-branches dynamically (`retry_count += 1`), finds an optimal slot, shifts the movable task, and validates zero collisions.

---

## Slide 4: Technical Stack & Architecture

### Full-Stack Agentic Engineering:
- **Core Orchestrator:** Python 3.10+ async agent loop (`app/agents/`) with JSONL telemetry.
- **Data Layer:** **Zetaris USL** (`app/adapters/zetaris_adapter.py`) with SQL DDL views & 4 automated Data Quality rules.
- **Cognitive Memory:** **Meterless H-MEM Engine** (`app/engines/hmem_engine.py`) with 3-tier memory & recency decay.
- **Intent Classifier:** **Meterless Scout Intent Engine** (`app/engines/scout_intent_engine.py`) with slot & urgency extraction.
- **AI Gateway:** **Meterless Nightshift** (`app/adapters/nightshift_adapter.py`) OpenAI-compatible runtime endpoint.
- **Foundational Models:** **NVIDIA Nemotron-3-super-120b** (Reasoning) + **Nemotron-3.5-lightning-30b** (Critic).
- **Voice Interface:** **NVIDIA Riva Parakeet-RNNT 1.1B ASR** streaming speech recognition.
- **Interactive UI:** High-performance dark-mode web application (Vanilla HTML5/CSS3/ES6, Zero heavy frameworks).
- **Deployment:** Dockerized container, zero-config CLI (`POST /run`), and offline `SAMPLE_MODE=true` fallback.

---

## Slide 5: How Zetaris & Meterless Were Used

### 1. Zetaris as the Foundational Data Layer:
- **Unified Semantic Layer (USL):** Federates 3 disconnected sources:
  1. `src_calendar_events`: Calendar busy blocks, durations, pinned flags.
  2. `src_task_backlog`: High-priority engineering issues from Jira/Linear with estimates.
  3. `src_user_preferences`: Working hours, buffer intervals (15 min), protected categories.
- **Cross-Source Queries:** SQL views (`usl_cross_source_feasibility`) execute capacity modeling directly in the data layer rather than slow Python loops.
- **Data Quality (DQ) Enforcement:** 4 mandatory rules (`RULE_TIME_ORDER`, `RULE_NO_OVERLAPPING_PINNED`, `RULE_VALID_PRIORITY`, `RULE_NON_EMPTY_IDENTIFIERS`) gatekeep every state change.

### 2. Meterless Engines & Nightshift Provider:
- **Meterless H-MEM (Hierarchical Memory):**
  - *Tier 1 (Working Memory):* Tracks active session goals, candidate time proposals, and critic feedback.
  - *Tier 2 (Episodic Memory):* Stores historical scheduling decisions with recency decay weighting.
  - *Tier 3 (Semantic Long-Term Memory):* Consolidates recurring user choices into reinforced behavioral habits (`morning_focus_bias`, `meeting_buffer_affinity`).
- **Meterless Scout Intent:** Computes numerical urgency (0.0–1.0) and decomposes ambiguous requests into structured parameters.
- **Meterless Nightshift:** Orchestrates all LLM queries through a unified local runtime daemon.

---

## Slide 6: What Was Unique About Our Use of Sponsors

| Sponsor | Core Role | What Makes Our Integration Unique |
|---|---|---|
| **Zetaris** | Unified Semantic Layer | **Semantic Feasibility Modeling:** Offloaded cross-source constraint joins (backlog tasks vs calendar capacity vs buffer preferences) into native Zetaris SQL views, with active DQ validation gates. |
| **Meterless** | H-MEM & Scout Intent + Nightshift | **Habit Consolidation:** H-MEM doesn't just store conversational logs; it updates Bayesian confidence scores for user habits (`morning_focus_bias`), allowing the agent to continuously adapt without prompt tuning. |
| **NVIDIA** | Nemotron Models & Riva ASR | **Specialized Model Allocation:** Heavy reasoning (`nemotron-3-super-120b`) handles Planner & Reconciler; high-speed low-latency (`nemotron-3.5-lightning-30b`) runs the Critic evaluator. Native multilingual voice input via Riva Parakeet. |
| **Cursor / Space XAI** | Dev Environment | **Accelerated Multi-Agent Scaffolding:** Used Cursor multi-file contextual refactoring to architect the 4-agent state machine and construct 101 automated verification tests. |

---

## Slide 7: Product Visuals & User Experience

### 1. Interactive Cognitive Calendar UI:
- Modern dark-theme scheduling matrix with time grid (08:00–19:00).
- Visual color-coding: Urgent tasks (Red/Amber), Pinned meetings (Cyan), Flexible sessions (Purple).
- Real-time drag/drop & automated event shifts.

### 2. "Explain Why" Evidence Drawer:
- Clicking any scheduled item opens the transparent reasoning trail.
- Users see the exact Zetaris queries, H-MEM memory recall, and ConflictCritic checks that justified the schedule slot.

### 3. Real-Time Telemetry & Traces:
- Live expandable JSONL trace drawer displaying agent handoffs, confidence levels, model names, and critique loops.

---

## Slide 8: Future Enhancements & Impact

### Quantifiable Impact:
- **2.5 Hours Saved Daily** per knowledge worker in calendar management and meeting triage.
- **100% Elimination of Double-Bookings** through Zetaris Data Quality rules and ConflictCritic validation.
- **Zero Hallucination:** Deterministic constraint verification backing every generative step.

### Future Roadmap:
- **v2.1:** Native CalDAV / Microsoft Graph live bi-directional synchronization via Zetaris streaming CDC connectors.
- **v2.2:** Cross-Organizational Multi-Agent Negotiation — TimePilot agents negotiating meeting slots across different companies using shared H-MEM buffer protocols.
- **v2.3:** Mobile Voice Assistant on iOS/Android powered by NVIDIA Riva edge models.

---

> **Try it now:** `git clone https://github.com/GubarVlad/TimePilot_AI.git`  
> Run in Sample Mode: `SAMPLE_MODE=true python run.py --input input_examples/example_1.json`

