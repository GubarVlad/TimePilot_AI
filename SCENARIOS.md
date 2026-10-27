# TimePilot AI — Natural Language Scheduling Scenarios Catalog

This catalog serves as the formal specification for system prompts, fallback rules, edge case testing, and verification. While external LLMs may experience variances, TimePilot AI's multi-agent architecture independently validates every proposed action against calendar state and Zetaris Data Quality rules. Ambiguous requests trigger clarifying questions rather than destructive or unintended modifications.

---

## 1. Calendar Inspection & Read-Only Queries

**Sample Inquiries:**
- *"What is on my schedule today?"*; *"Show plan for tomorrow"*; *"What is scheduled for next Friday?"*
- *"What is next?"*; *"When does the team sync meeting start?"*
- *"How busy is my day?"*; *"How many hours of meetings do I have this week?"*
- *"Which tasks are urgent?"*; *"Which items from today's list are already completed?"*
- *"Find a 45-minute free window"*; *"When is there half an hour for a call today?"*
- *"Can I schedule a meeting at 15:00?"* — Evaluates slot feasibility without modifying state until confirmed.
- *"What happens if I postpone the review?"* / *"How should I rearrange my morning?"* — Analytical simulation only.

---

## 2. Scheduling Single Tasks

**Sample Requests:**
- *"Schedule presentation prep tomorrow at 10:00 for 90 minutes."*
- *"Plan a 30-minute walk on Sunday."*
- *"Urgent: submit commercial proposal today before 16:00."*
- *"Add an afternoon coffee break for 15 minutes."*
- *"Create a meeting with Ira on Wednesday at 12:30 for 45 minutes."*
- *"Record project delivery milestone on 2026-11-05 at 18:00."*
- *"Add a task to call the medical clinic"* — Treated as an internal task, not a real external booking.
- *"Book me a dentist appointment"* — Protects user safety: refuses to fake external booking, asks user to confirm actual clinic slot first.

**Core Rules:**
- Dates are normalized relative to current day.
- Explicit duration takes precedence over defaults; default task length is 60 minutes.
- The agent never hallucinates participants, addresses, or false external confirmations.

---

## 3. Batch Task Scheduling

**Sample Requests:**
- *"Tomorrow schedule: email triage at 9 for 20m, report at 10 for 1 hour, and slide deck at 12 for 90m."*
- *"Add three afternoon items: pay invoice, prepare slides, write client follow-up. Make payment urgent."*
- *"Schedule deep work and two 10-minute breaks; only the deep work session should be high priority."*

**Core Rules:**
- Atomic verification: if any item in a batch produces an unresolvable collision, the agent flags the conflict and suggests alternatives.
- Priorities, descriptions, and durations are bound to specific items and not inadvertently inherited across siblings.

---

## 4. Editing & Modifying Existing Events

### Title & Description
- *"Rename 'Project Prep' to 'Client Presentation Review'"*
- *"Update description for 'Weekly Sync' to 'Review Q4 hiring pipeline'"*

### Date & Time Adjustments
- *"Move 'Design Sync' to 15:00"* — Preserves original date and duration.
- *"Postpone 'Contract Review' to tomorrow"* — Preserves original time and duration.
- *"Extend 'Strategy Session' to 2 hours"* — Extends end time, verifying subsequent buffers.

---

## 5. Conflict Resolution & Self-Correction

- When an urgent task arrives that collides with a flexible task, `ConflictCritic` detects the overlap.
- `ContextAgent` identifies movable tasks versus immutable/pinned commitments (such as doctor visits or client presentations).
- The system automatically shifts movable tasks forward and explains the rationale via **"Explain Why"**.
- Immovable and protected events (`category IN ('medical', 'doctor', 'flight')`) are strictly protected from modification.
