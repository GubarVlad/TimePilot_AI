# TimePilot AI — Autonomous Cognitive Calendar & Scheduling Agent

[![Open Agent Hackathon 2026](https://img.shields.io/badge/Open%20Agent%20Hackathon-2026-brightgreen.svg)](https://hackathon.genai.works)
[![Zetaris USL](https://img.shields.io/badge/Data%20Layer-Zetaris%20USL-blue.svg)](https://www.zetaris.com/)
[![Meterless Engines](https://img.shields.io/badge/Engines-Meterless%20H--MEM%20%26%20Scout%20Intent-purple.svg)](https://meterless.io/)
[![Meterless Nightshift](https://img.shields.io/badge/AI%20Provider-Meterless%20Nightshift-orange.svg)](https://meterless.io/)
[![NVIDIA Nemotron](https://img.shields.io/badge/Models-NVIDIA%20Nemotron%20%26%20Parakeet-76B900.svg)](https://build.nvidia.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Open Agent Hackathon 2026 Submission**  
> **Track:** Track 02 (The Agent That Can Explain Why) & Track 03 (Reasoning Architecture) | **Bonus:** Tinkerer (Bring Your Own Project)  
> **Mission:** *Not another chatbot. An agent that does real work.*

---

## Table of Contents
- [1. Problem & Solution Overview](#1-problem--solution-overview)
- [2. Multi-Agent Reasoning Architecture](#2-multi-agent-reasoning-architecture)
- [3. Sponsor Technology Integrations](#3-sponsor-technology-integrations)
  - [Zetaris Unified Semantic Layer (USL)](#31-zetaris-unified-semantic-layer-usl)
  - [Meterless Engines: H-MEM & Scout Intent](#32-meterless-engines-h-mem--scout-intent)
  - [Meterless Nightshift (Primary AI Provider)](#33-meterless-nightshift-primary-ai-provider)
  - [NVIDIA Nemotron & Riva Parakeet ASR](#34-nvidia-nemotron--riva-parakeet-asr)
- [4. Quick Start (Clean Setup)](#4-quick-start-clean-setup)
  - [Option A: Running with Docker (Recommended)](#option-a-running-with-docker-recommended)
  - [Option B: Running with Python Virtualenv](#option-b-running-with-python-virtualenv)
- [5. Programmatic Driving (`POST /run` & CLI)](#5-programmatic-driving-post-run--cli)
- [6. Sample Mode (`SAMPLE_MODE=true`)](#6-sample-mode-sample_modetrue)
- [7. Sample Inputs & Outputs](#7-sample-inputs--outputs)
- [8. Traces & Observability](#8-traces--observability)
- [9. Testing & Conformance Verification](#9-testing--conformance-verification)
- [10. Limitations & Future Enhancements](#10-limitations--future-enhancements)

---

## 1. Problem & Solution Overview

### The Problem
Traditional calendars are static, siloed databases. When urgent tasks arise, users face fragmented intelligence:
- Unscheduled high-priority tasks sit forgotten in **task backlogs (Jira/Linear)**.
- Calendar commitments lack semantic awareness of **meeting buffers**, **energy curves**, and **protected appointments (medical/travel)**.
- Existing AI tools act as simple linear chat wrappers that hallucinate slots, overwrite immovable commitments, and cannot **explain why** a decision was made.

### The Solution: TimePilot AI
TimePilot AI is an autonomous, context-aware scheduling agent that:
1. **Unifies fragmented data sources** via **Zetaris Unified Semantic Layer (USL)** (calendar schedule + task backlog + user energy/buffer rules).
2. **Retains memory and habits** via **Meterless H-MEM** (working memory, episodic decisions, and consolidated semantic habits).
3. **Discovers implicit goals and urgency** via **Meterless Scout Intent Engine**.
4. **Executes a self-correcting critique loop** (`PlannerAgent` → `ContextAgent` → `ConflictCritic` → `ReconcilerAgent`).
5. **Provides evidence-backed explanations ("Explain Why")** for every single modification.

---

## 2. Multi-Agent Reasoning Architecture

TimePilot AI rejects fixed, fragile chains (`A -> B -> C`). Instead, it executes an iterative, collaborative multi-agent loop with active critique, constraint evaluation, and branching retries:

```
                  ┌──────────────────────────────────────────────┐
                  │             User / API / Voice                │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │               PlannerAgent                   │
                  │  (Scout Intent, Urgency & Slot Analysis)     │
                  └──────────────────────┬───────────────────────┘
                                         │ delegate
                                         ▼
┌─────────────────────────┐       ┌──────────────────────────────┐
│  Zetaris USL (Data)     │◄─────►│        ContextAgent          │
│  - src_calendar_events  │       │  (Zetaris USL + H-MEM Memory)│
│  - src_task_backlog     │       └──────────────┬───────────────┘
│  - src_user_preferences │                      │ propose slot
└─────────────────────────┘                      ▼
┌─────────────────────────┐       ┌──────────────────────────────┐
│  Meterless H-MEM        │◄─────►│       ConflictCritic         │
│  - Tier 1: Working Mem  │       │  (EvaluatorAgent & Data Qual)│
│  - Tier 2: Episodic Mem │       └──────────────┬───────────────┘
│  - Tier 3: Semantic LTM │                      │
└─────────────────────────┘      [Collides?]     ├────────────► [Reject & Retry]
                                                 │              Branch to ContextAgent
                                                 │ [Approved]   with adjusted constraints
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │       ReconcilerAgent        │
                                  │  - Synthesizes Action Plan   │
                                  │  - Generates 'Explain Why'   │
                                  │  - Commits H-MEM Episode     │
                                  │  - Updates Zetaris USL       │
                                  └──────────────┬───────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │    Structured Result & UI    │
                                  └──────────────────────────────┘
```

---

## 3. Sponsor Technology Integrations

### 3.1 Zetaris Unified Semantic Layer (USL)
- **Role:** Foundational Data Layer.
- **Implementation:** `app/adapters/zetaris_adapter.py` & `data/zetaris_usl_ddl.sql`.
- **Three Onboarded Data Sources:**
  1. `src_calendar_events`: Calendar commitments, times, mobility (`movable`, `fixed`).
  2. `src_task_backlog`: Engineering issues from Jira/Linear, estimates, priorities, due dates.
  3. `src_user_preferences`: Work hours, focus windows, minimum meeting buffers (15 min), and protected categories (`medical`, `dentist`, `flight`).
- **Active Cross-Source Queries:**
  - `usl_unified_schedule`: Joins events with user buffer rules and computes `is_immutable`.
  - `usl_cross_source_feasibility`: Computes backlog task feasibility against remaining daily free capacity.
  - `find_free_focus_slots`: Detects focus windows without violating meeting buffers.
- **Data Quality (DQ) Enforcement:** Runs 4 automated rules (`RULE_TIME_ORDER`, `RULE_NO_OVERLAPPING_PINNED`, `RULE_VALID_PRIORITY`, `RULE_NON_EMPTY_IDENTIFIERS`) before any changes are committed.
- **Full Reflection Document:** See [docs/ZETARIS_USL.md](docs/ZETARIS_USL.md) for use case documentation, exploratory queries, time savings comparison, and PM product proposal.

### 3.2 Meterless Engines: H-MEM & Scout Intent
- **Engine 1 — H-MEM (Hierarchical Memory):** `app/engines/hmem_engine.py`
  - **Tier 1 (Working Memory):** Tracks in-turn candidate slots, goals, and critic feedback.
  - **Tier 2 (Episodic Memory):** Stores past scheduling episodes with recency decay weighting.
  - **Tier 3 (Semantic Long-Term Memory):** Consolidates accepted actions into reinforced user habits (`morning_focus_bias`, `meeting_buffer_affinity`, `protected_lunch_window`, `flexible_task_shift_preference`).
- **Engine 2 — Scout Intent:** `app/engines/scout_intent_engine.py`
  - Classifies user intent (`SCHEDULE_NEW_TASK`, `RESOLVE_CONFLICT`, `OPTIMIZE_DAY`, `EXPLAIN_WHY`, `QUERY_FREE_TIME`), computes urgency (0.0–1.0), and extracts temporal slots.
- **Passing Test:** Run `python3 -m unittest tests/test_meterless_engine.py`.

### 3.3 Meterless Nightshift (Primary AI Provider)
- **Role:** Primary OpenAI-compatible AI gateway (`app/adapters/nightshift_adapter.py`).
- **Configuration:** Points to `METERLESS_BASE_URL` (`http://127.0.0.1:8088/v1`) using `METERLESS_RUNTIME_TOKEN`.
- **Models:** Primary reasoning routes through `METERLESS_MODEL=nvidia/nemotron-3-super-120b-a12b`.
- **Fault-Tolerant Fallback:** In `SAMPLE_MODE=true` or during connectivity disruptions, seamlessly runs local deterministic multi-agent synthesis while preserving trace telemetry.

### 3.4 NVIDIA Nemotron & Riva Parakeet ASR
- **NVIDIA Nemotron via Nightshift:**
  - `nvidia/nemotron-3-super-120b-a12b`: High-capability reasoning model driving `PlannerAgent`, `ContextAgent`, and `ReconcilerAgent`.
  - `nvidia/nemotron-3.5-lightning-30b-a3b`: Low-latency evaluation model powering `ConflictCritic`.
- **NVIDIA Riva / Parakeet Multilingual ASR:**
  - Streaming multilingual speech-to-text (`Parakeet-RNNT 1.1B Multilingual` via `grpc.nvcf.nvidia.com:443`). Enables hands-free voice scheduling directly in Russian and English.
- **Sponsor Explanation:** See [docs/SPONSOR_TECH.md](docs/SPONSOR_TECH.md) for full details.

---

## 4. Quick Start (Clean Setup)

### Option A: Running with Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/vladgubar/TimePilot_AI.git
cd TimePilot_AI

# 2. Setup environment variables (placeholders by default)
cp .env.example .env

# 3. Build Docker container
docker build -t oah-submission .

# 4. Run container (mapped to port 8000)
# Inside Docker Desktop, host services can be reached via host.docker.internal
docker run --rm -p 8000:8000 --env-file .env oah-submission
```

The application is now accessible at `http://localhost:8000` (Web UI & REST API).

### Option B: Running with Python Virtualenv

Requires **Python 3.10+**.

```bash
# 1. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment configuration
cp .env.example .env

# 4. Start TimePilot AI
python run.py --serve --port 8000
```

---

## 5. Programmatic Driving (`POST /run` & CLI)

Judges can drive TimePilot AI programmatically without navigating the UI:

### Programmatic HTTP Endpoint (`POST /run`)
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d @input_examples/example_1.json
```

### Direct CLI Execution
```bash
python run.py --input input_examples/example_1.json --output output.json
```

**Response Format:**
```json
{
  "status": "success",
  "reply": "Запланировал «Аудит утечки токенов безопасности» на 2026-10-27 в 15:00–15:45...",
  "plan": "Scheduled 'Аудит утечки токенов безопасности' (15:00-15:45)",
  "explanation_why": "1. Анализ цели (Scout Intent)... 2. Источники данных (Zetaris USL)... 3. Память (H-MEM)... 4. Верификация (ConflictCritic)...",
  "actions": [
    {
      "action": "create_event",
      "event": { "id": "tp-...", "title": "Аудит утечки токенов безопасности", "start": "15:00", "end": "15:45", ... }
    },
    {
      "action": "move_event",
      "title": "UI Prototyping & Review",
      "from_start": "15:30",
      "to_start": "15:45"
    }
  ],
  "traces_count": 6,
  "zetaris_usl": {
    "data_quality_rules_passed": 4,
    "sources_queried": ["src_calendar_events", "src_task_backlog", "src_user_preferences"],
    "events_analyzed": 6,
    "urgent_tasks_count": 3
  },
  "meterless_engine": {
    "engine": "H-MEM + Scout Intent",
    "working_memory_active": true,
    "episodes_recalled": 2,
    "semantic_habits_applied": ["morning_focus_bias", "meeting_buffer_affinity"]
  },
  "ai_provider": {
    "provider": "Meterless Nightshift",
    "primary_model": "nvidia/nemotron-3-super-120b-a12b",
    "eval_model": "nvidia/nemotron-3.5-lightning-30b-a3b"
  }
}
```

---

## 6. Sample Mode (`SAMPLE_MODE=true`)

Judges may not have live Zetaris REST servers or Meterless Nightshift runtime daemons active on their evaluation machines.  
**TimePilot AI includes a first-class `SAMPLE_MODE=true` fallback:**
- Runs from a fresh clone with an empty `.env`.
- Executes **real multi-agent reasoning** on cached Zetaris semantic tables and H-MEM memories (not static mock replays).
- Runs the 4-agent collaborative loop, validates 4 Zetaris Data Quality rules, checks calendar conflicts, and emits real JSONL trace logs.

To test Sample Mode with Zetaris and Nightshift stopped:
```bash
SAMPLE_MODE=true python run.py --input input_examples/example_1.json
```

---

## 7. Sample Inputs & Outputs

The project includes 3 realistic end-to-end evaluation examples:

| Input File | Description | Key Agent Behavior Shown | Matching Output |
|---|---|---|---|
| [`input_examples/example_1.json`](input_examples/example_1.json) | Urgent security audit task arriving at 14:00 | ConflictCritic detects collision with Team Sync, branches to retry, shifts movable UI session, assigns 15:00–15:45 | [`output_examples/example_1.json`](output_examples/example_1.json) |
| [`input_examples/example_2.json`](input_examples/example_2.json) | Daily schedule optimization request | Queries Zetaris USL backlog urgency, cross-joins with free capacity, aligns with morning focus habit (08:30–09:30) | [`output_examples/example_2.json`](output_examples/example_2.json) |
| [`input_examples/example_3.json`](input_examples/example_3.json) | Request for a 90-minute focus window | Respects protected medical appointments, avoids lunch window, shifts flexible afternoon task to 17:00–18:30 | [`output_examples/example_3.json`](output_examples/example_3.json) |

---

## 8. Traces & Observability

Every agent action and handoff is logged in real-time to stdout and appended to `logs/agent_traces.jsonl`.

### Sample Log Trace (JSONL format):
```json
{"timestamp":"2026-10-27T08:26:08.486408Z","agent_name":"PlannerAgent","action":"delegate","input_summary":"User request: 'Срочно добавь аудит утечки токенов...'","output_summary":"Delegated context retrieval to ContextAgent","target_agent":"ContextAgent","model":"nvidia/nemotron-3-super-120b-a12b","confidence":0.96,"retry_count":0,"status":"success"}
{"timestamp":"2026-10-27T08:26:08.487217Z","agent_name":"ContextAgent","action":"provide_context","input_summary":"Retrieval for date=2026-10-27, dur=45m","output_summary":"Zetaris returned 6 events, 3 backlog items. Proposing slot 14:00-14:45","target_agent":"ConflictCritic","model":"nvidia/nemotron-3-super-120b-a12b","confidence":0.91,"retry_count":0,"status":"success"}
{"timestamp":"2026-10-27T08:26:08.487404Z","agent_name":"ConflictCritic","action":"critique","input_summary":"Audit candidate slot 14:00-14:45","output_summary":"Candidate slot 14:00-14:45 collides with 'Team Project Sync'. Requires revision after 15:00","target_agent":"ContextAgent","model":"nvidia/nemotron-3.5-lightning-30b-a3b","confidence":0.86,"retry_count":0,"status":"needs_revision"}
{"timestamp":"2026-10-27T08:26:08.487651Z","agent_name":"ContextAgent","action":"provide_context","input_summary":"Retrieval for date=2026-10-27, dur=45m (retry=1)","output_summary":"Adjusted proposal based on critique. Proposing slot 15:00-15:45","target_agent":"ConflictCritic","model":"nvidia/nemotron-3-super-120b-a12b","confidence":0.91,"retry_count":1,"status":"success"}
{"timestamp":"2026-10-27T08:26:08.487800Z","agent_name":"ConflictCritic","action":"approve","input_summary":"Validated slot 15:00-15:45 (retry=1)","output_summary":"Approved slot 15:00-15:45. Validated against 6 events, Zetaris DQ checks (4/4 passed)","target_agent":"ReconcilerAgent","model":"nvidia/nemotron-3.5-lightning-30b-a3b","confidence":0.96,"retry_count":1,"status":"success"}
{"timestamp":"2026-10-27T08:26:08.488047Z","agent_name":"ReconcilerAgent","action":"synthesize_plan","input_summary":"Approved slot 15:00-15:45 for 'Аудит утечки'","output_summary":"Emitted plan with 2 actions. Updated Zetaris USL and H-MEM","target_agent":"User","model":"nvidia/nemotron-3-super-120b-a12b","confidence":0.98,"retry_count":0,"status":"success"}
```

---

## 9. Testing & Conformance Verification

To run the complete test suite:

```bash
# Run all tests (101 unit, integration, and conformance tests)
PYTHONPATH=. python3 -m unittest discover tests

# Run Meterless Engine Conformance Test (H-MEM & Scout Intent)
PYTHONPATH=. python3 tests/test_meterless_engine.py

# Run Zetaris USL Evaluation Test (Sources, Queries & Data Quality)
PYTHONPATH=. python3 tests/test_zetaris_usl.py

# Run Multi-Agent Orchestrator Loop Test
PYTHONPATH=. python3 tests/test_agent_orchestrator.py

# Run Programmatic Entry Point Test
PYTHONPATH=. python3 tests/test_run_endpoint.py
```

All 101 tests pass with 0 errors.

---

## 10. Limitations & Future Enhancements

### Current Limitations
1. **Recurring Series Editing:** While individual recurring instances are represented as calendar records, updating an infinite recurring series as a single atomic macro action is planned for v2.1.
2. **External CalDAV Synchronization:** The Zetaris USL currently unifies local JSON schedule repositories, task backlog, and preferences. Live bi-directional CalDAV synchronization with Google Calendar / MS Exchange will be enabled once Zetaris streaming CDC connectors are released.
3. **Medical Appointment Booking:** For security and compliance, TimePilot AI refuses to simulate real-world medical or financial bookings without user out-of-band confirmation, treating medical events as strictly protected and immutable.

### Future Enhancements
- **Zetaris Reactive USL Subscriptions:** Streaming change-data-capture to trigger proactive schedule rebalancing in real-time when external calendar invites change.
- **Multi-User Team Coordination:** Expanding H-MEM to model team-wide energy curves and cross-organizational meeting buffer negotiation.
