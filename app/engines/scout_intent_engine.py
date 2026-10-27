from __future__ import annotations

import re
from typing import Any


class ScoutIntentEngine:
    """Meterless Scout Intent Engine.
    
    Provides intent discovery, temporal entity extraction, ambiguity scoring,
    and constraint detection for autonomous agent planning.
    Distinguishes between scheduling/mutation intents and informational queries.
    """

    def analyze(self, user_message: str, current_date: str) -> dict[str, Any]:
        text = user_message.strip().lower()

        # 1. Detect Intent Category
        intent_type = "GENERAL_CONVERSATION"
        confidence = 0.85
        
        # Rhythm, habits, and profile queries
        if re.search(
            r"(?:^|[^\w])(what do you know about|tell me about|how is my|what is my|explain my|analyze my|know about)\s*(my\s*)?(bio[- ]?rhythms?|rhythms?|habits?|energy curve|chronotype|about me|биоритм\w*|ритм\w*|привычк\w*|обо мне)(?:[^\w]|$)",
            text,
        ) or re.search(
            r"(?:^|[^\w])(what do you know|tell me what you know)(?:[^\w]|$)",
            text,
        ):
            intent_type = "QUERY_RHYTHM"
            confidence = 0.96
        # Schedule inspection queries
        elif re.search(
            r"(?:^|[^\w])(what is (?:on|scheduled)|show (?:me\s+)?(?:plan|schedule)|how busy|what do i have|what's next|что у меня|покажи расписание|план на|насколько занят)(?:[^\w]|$)",
            text,
        ):
            intent_type = "QUERY_SCHEDULE"
            confidence = 0.94
        # Free time & focus slot exploration
        elif re.search(
            r"(?:^|[^\w])(free window|free slot|free time|available|when do i have|find time|find (?:a\s+)?.*?(?:slot|window|time)|deep focus|focus slot|focus window|focus time|окно|свободн\w*|когда есть|найди время)(?:[^\w]|$)",
            text,
        ):
            intent_type = "QUERY_FREE_TIME"
            confidence = 0.94
        # Analytical Explain Why
        elif re.search(
            r"(?:^|[^\w])(why|explain|reason|how come|justification|почему|объясни|зачем|обоснуй)(?:[^\w]|$)",
            text,
        ):
            intent_type = "EXPLAIN_WHY"
            confidence = 0.95
        # Optimization
        elif re.search(
            r"(?:^|[^\w])(optimize|rebalance|reorganize|balance|reschedule day|clean up|оптимизир\w*|разгрузи\w*|наведи порядок)(?:[^\w]|$)",
            text,
        ):
            intent_type = "OPTIMIZE_DAY"
            confidence = 0.93
        # Conflict resolution / shift
        elif re.search(
            r"(?:^|[^\w])(conflict|overlap|clash|shift|move|postpone|delay|конфликт\w*|накладк\w*|пересечен\w*|сдвинь\w*|перенеси\w*)(?:[^\w]|$)",
            text,
        ):
            intent_type = "RESOLVE_CONFLICT"
            confidence = 0.92
        # Explicit scheduling
        elif re.search(
            r"(?:^|[^\w])(schedule|add|create|book|insert|plan|set up|добавь|создай|запланируй|поставь|запиши|внести|внеси)(?:[^\w]|$)",
            text,
        ):
            intent_type = "SCHEDULE_NEW_TASK"
            confidence = 0.96
        # Constraints & pins
        elif re.search(
            r"(?:^|[^\w])(lock|pin|freeze|fix|don't move|do not move|protected|immutable|заклей|закрепи|зафиксируй|не двигай)(?:[^\w]|$)",
            text,
        ):
            intent_type = "UPDATE_CONSTRAINTS"
            confidence = 0.91

        # Determine if this intent authorizes creating or modifying calendar events
        is_scheduling_intent = intent_type in {
            "SCHEDULE_NEW_TASK",
            "OPTIMIZE_DAY",
            "RESOLVE_CONFLICT",
            "UPDATE_CONSTRAINTS",
        }

        # 2. Extract Urgency & Priority
        urgency_score = 0.5
        priority = "medium"
        if re.search(
            r"(?:^|[^\w])(urgent|asap|critical|emergency|high priority|срочн\w*|критичн\w*|горим\w*|немедленн\w*)(?:[^\w]|$)",
            text,
        ):
            urgency_score = 0.95
            priority = "urgent"
        elif re.search(
            r"(?:^|[^\w])(important|high|priority|важно|важный|важная|высокий|приоритетн\w*)(?:[^\w]|$)",
            text,
        ):
            urgency_score = 0.8
            priority = "high"
        elif re.search(
            r"(?:^|[^\w])(security|audit|compliance|vulnerability|breach|incident|outage|hotfix|patch|production|критическ\w*|уязвимост\w*|инцидент\w*)(?:[^\w]|$)",
            text,
        ):
            urgency_score = 0.75
            priority = "high"
        elif re.search(
            r"(?:^|[^\w])(low|minor|whenever|optional|low priority|низк\w*|не к спеху|когда будет время)(?:[^\w]|$)",
            text,
        ):
            urgency_score = 0.2
            priority = "low"

        # 3. Extract Duration
        duration_minutes = 60
        m_dur_hours = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:-?\s*h|-?\s*hr|-?\s*hrs|-?\s*hour|-?\s*hours|ч|час|часа|часов)", text)
        m_dur_half = re.search(r"(?:for\s+)?(?:an\s+hour\s+and\s+a\s+half|1\.5\s*(?:h|hr|hours)|полтора\s*часа)", text)
        m_dur_mins = re.search(r"(?:for\s+)?(\d+)\s*(?:min|mins|minute|minutes|мин|минут|минуты)", text)

        if m_dur_half:
            duration_minutes = 90
        elif m_dur_hours:
            val = float(m_dur_hours.group(1).replace(",", "."))
            duration_minutes = int(val * 60)
        elif m_dur_mins:
            duration_minutes = int(m_dur_mins.group(1))

        # 4. Extract Explicit Time (supports 14:00, 2 PM, 2:30 pm, в 14:00)
        time_hint = None
        m_time_12h = re.search(r"\b(?:at|в|к|c|с)?\s*([01]?\d)(?::([0-5]\d))?\s*(am|pm)\b", text, re.IGNORECASE)
        if m_time_12h:
            h = int(m_time_12h.group(1))
            m = int(m_time_12h.group(2) or 0)
            meridiem = m_time_12h.group(3).lower()
            if meridiem == "pm" and h < 12:
                h += 12
            elif meridiem == "am" and h == 12:
                h = 0
            time_hint = f"{h:02d}:{m:02d}"
        else:
            m_time = re.search(r"\b(?:at|in|в|c|с)\s*([012]?\d:[0-5]\d)\b", text)
            if m_time:
                time_hint = m_time.group(1)
                if len(time_hint) == 4:
                    time_hint = "0" + time_hint
            else:
                m_simple_time = re.search(r"\b(?:at|в|к)\s*([012]?\d)(?:\s*(?:ч|час|часов|:00))?\b", text)
                if m_simple_time:
                    h = int(m_simple_time.group(1))
                    if 0 <= h <= 23:
                        time_hint = f"{h:02d}:00"

        # 5. Extract Title Candidate
        cleaned = re.sub(
            r"^(?:urgent[:\s]+|urgent|please\s+|schedule\s+|add\s+|create\s+|book\s+|plan\s+|добавь\s+|создай\s+|поставь\s+|запланируй\s+|запиши\s+|внеси\s+)",
            "",
            text,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"\s+(?:tomorrow|today|at\s+\d{1,2}(?::\d{2})?|for\s+\d+\s*(?:min|mins|minutes|h|hours)|urgent|important|asap|завтра|сегодня|в\s+\d{1,2}(?::\d{2})?|на\s+\d+\s*(?:мин|час|минут)).*$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        ).strip()
        title_candidate = cleaned.capitalize() if cleaned else "Scheduled Task"

        # 6. Ambiguity Analysis
        ambiguity_score = 0.1
        if intent_type == "SCHEDULE_NEW_TASK" and not time_hint and "tomorrow" not in text and "today" not in text and "завтра" not in text and "сегодня" not in text:
            ambiguity_score = 0.4
        if len(user_message.strip()) < 4:
            ambiguity_score = 0.9

        return {
            "intent_type": intent_type,
            "is_scheduling_intent": is_scheduling_intent,
            "confidence": confidence,
            "urgency_score": urgency_score,
            "priority": priority,
            "duration_minutes": duration_minutes,
            "time_hint": time_hint,
            "title_candidate": title_candidate,
            "ambiguity_score": ambiguity_score,
            "requires_clarification": ambiguity_score > 0.75,
            "raw_message": user_message,
        }
