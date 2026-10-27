from __future__ import annotations

import datetime as dt
import json
import os
import sqlite3
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"


class ZetarisUSLAdapter:
    """Zetaris Unified Semantic Layer (USL) Adapter.
    
    Serves as the data layer for TimePilot AI.
    Integrates 3 fragmented data sources:
      1. Calendar Events (src_calendar_events)
      2. Task Backlog (src_task_backlog)
      3. User Preferences & Biological Energy (src_user_preferences)
      
    Provides REST client communication to Zetaris server, with full
    in-memory relational SQL semantic simulation when in SAMPLE_MODE=true
    or when Zetaris server is offline.
    """

    def __init__(
        self,
        rest_url: Optional[str] = None,
        org_id: Optional[str] = None,
        api_key: Optional[str] = None,
        sample_mode: Optional[bool] = None,
    ):
        self.rest_url = (rest_url or os.getenv("ZETARIS_REST_URL", "http://localhost:8888/api/v1.0")).rstrip("/")
        self.org_id = org_id or os.getenv("ZETARIS_ORG_ID", "1")
        self.api_key = api_key or os.getenv("ZETARIS_API_KEY", "")
        
        env_sample = os.getenv("SAMPLE_MODE", "true").lower() in ("true", "1", "yes")
        self.sample_mode = sample_mode if sample_mode is not None else env_sample
        
        # Local SQLite in-memory database acting as USL execution engine
        self._db = sqlite3.connect(":memory:", check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._init_usl_schema()
        self._load_sources_into_usl()

    def _init_usl_schema(self) -> None:
        """Initialize USL DDL schema and views."""
        ddl_path = DATA_DIR / "zetaris_usl_ddl.sql"
        if ddl_path.exists():
            ddl_sql = ddl_path.read_text(encoding="utf-8")
        else:
            ddl_sql = """
            CREATE TABLE IF NOT EXISTS src_calendar_events (
                id VARCHAR(64) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                event_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                priority VARCHAR(32) DEFAULT 'medium',
                category VARCHAR(64) DEFAULT 'task',
                description TEXT,
                fixed BOOLEAN DEFAULT FALSE,
                mobility VARCHAR(32) DEFAULT 'movable',
                status VARCHAR(32) DEFAULT 'planned',
                source VARCHAR(32) DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS src_task_backlog (
                task_id VARCHAR(64) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                estimated_minutes INTEGER NOT NULL,
                priority VARCHAR(32) NOT NULL,
                due_date DATE NOT NULL,
                category VARCHAR(64) DEFAULT 'engineering',
                status VARCHAR(32) DEFAULT 'todo',
                assignee VARCHAR(64) DEFAULT 'user_default',
                context_tags TEXT,
                description TEXT
            );
            CREATE TABLE IF NOT EXISTS src_user_preferences (
                user_id VARCHAR(64) PRIMARY KEY,
                name VARCHAR(128) NOT NULL,
                timezone VARCHAR(64) DEFAULT 'UTC',
                work_start_time TIME NOT NULL,
                work_end_time TIME NOT NULL,
                min_buffer_minutes INTEGER DEFAULT 15,
                focus_window_start TIME DEFAULT '09:00',
                focus_window_end TIME DEFAULT '12:00',
                lunch_window_start TIME DEFAULT '12:30',
                lunch_window_end TIME DEFAULT '13:45',
                protected_categories TEXT DEFAULT 'medical,dentist,flight,client_contract'
            );
            """
        with self._db:
            self._db.executescript(ddl_sql)

    def _load_sources_into_usl(self) -> None:
        """Load data from the 3 sources into the semantic tables."""
        # 1. Calendar events
        events_file = DATA_DIR / "calendar_events.json"
        if not events_file.exists():
            events_file = DATA_DIR / "events.json"
        if events_file.exists():
            try:
                content = json.loads(events_file.read_text(encoding="utf-8"))
                events = content.get("events", []) if isinstance(content, dict) else content
                with self._db:
                    self._db.execute("DELETE FROM src_calendar_events")
                    for ev in events:
                        self._db.execute(
                            """
                            INSERT OR REPLACE INTO src_calendar_events 
                            (id, title, event_date, start_time, end_time, priority, category, description, fixed, mobility, status, source)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                str(ev.get("id")),
                                str(ev.get("title", "")),
                                str(ev.get("date", "")),
                                str(ev.get("start", "")),
                                str(ev.get("end", "")),
                                str(ev.get("priority", "medium")),
                                str(ev.get("category", "task")),
                                str(ev.get("description", "")),
                                bool(ev.get("fixed", False)),
                                str(ev.get("mobility", "movable")),
                                str(ev.get("status", "planned")),
                                str(ev.get("source", "manual")),
                            ),
                        )
            except Exception as exc:
                print(f"[ZetarisUSL] Warning loading calendar_events: {exc}")

        # 2. Task backlog
        backlog_file = DATA_DIR / "task_backlog.json"
        if backlog_file.exists():
            try:
                content = json.loads(backlog_file.read_text(encoding="utf-8"))
                tasks = content.get("tasks", []) if isinstance(content, dict) else content
                with self._db:
                    self._db.execute("DELETE FROM src_task_backlog")
                    for t in tasks:
                        tags_str = ",".join(t.get("context_tags", [])) if isinstance(t.get("context_tags"), list) else str(t.get("context_tags", ""))
                        self._db.execute(
                            """
                            INSERT OR REPLACE INTO src_task_backlog
                            (task_id, title, estimated_minutes, priority, due_date, category, status, assignee, context_tags, description)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                str(t.get("task_id")),
                                str(t.get("title", "")),
                                int(t.get("estimated_minutes", 60)),
                                str(t.get("priority", "medium")),
                                str(t.get("due_date", "")),
                                str(t.get("category", "engineering")),
                                str(t.get("status", "todo")),
                                str(t.get("assignee", "user_default")),
                                tags_str,
                                str(t.get("description", "")),
                            ),
                        )
            except Exception as exc:
                print(f"[ZetarisUSL] Warning loading task_backlog: {exc}")

        # 3. User preferences
        pref_file = DATA_DIR / "user_preferences.json"
        if pref_file.exists():
            try:
                p = json.loads(pref_file.read_text(encoding="utf-8"))
                with self._db:
                    self._db.execute("DELETE FROM src_user_preferences")
                    self._db.execute(
                        """
                        INSERT OR REPLACE INTO src_user_preferences
                        (user_id, name, timezone, work_start_time, work_end_time, min_buffer_minutes, 
                         focus_window_start, focus_window_end, lunch_window_start, lunch_window_end, protected_categories)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(p.get("user_id", "user_default")),
                            str(p.get("name", "Default User")),
                            str(p.get("timezone", "UTC")),
                            str(p.get("work_hours", {}).get("start", "08:30")),
                            str(p.get("work_hours", {}).get("end", "18:30")),
                            int(p.get("buffer_rules", {}).get("min_buffer_minutes_between_meetings", 15)),
                            str(p.get("focus_time", {}).get("preferred_start", "09:00")),
                            str(p.get("focus_time", {}).get("preferred_end", "12:00")),
                            str(p.get("lunch_window", {}).get("start", "12:30")),
                            str(p.get("lunch_window", {}).get("end", "13:45")),
                            ",".join(p.get("protected_event_types", ["medical", "dentist", "flight"])),
                        ),
                    )
            except Exception as exc:
                print(f"[ZetarisUSL] Warning loading user_preferences: {exc}")

    # =========================================================================
    # ZETARIS REST QUERY EXECUTION & SAMPLE FALLBACK
    # =========================================================================
    def execute_query(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        """Execute SQL query against live Zetaris endpoint or in-memory USL."""
        if not self.sample_mode and self.api_key:
            try:
                payload = json.dumps({"sql": sql, "org_id": self.org_id}).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.rest_url}/query",
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data.get("rows", [])
            except Exception as exc:
                # Fallback to local USL simulation
                pass

        # In-memory USL Execution
        cur = self._db.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    # =========================================================================
    # EXPLORATORY QUERIES (2-3 per Source)
    # =========================================================================
    # --- Source 1: Calendar Events ---
    def query_calendar_events_by_date(self, event_date: str) -> list[dict[str, Any]]:
        sql = """
        SELECT id, title, event_date, start_time, end_time, priority, category, fixed, mobility, status
        FROM src_calendar_events
        WHERE event_date = ?
        ORDER BY start_time ASC;
        """
        return self.execute_query(sql, (event_date,))

    def query_pinned_or_protected_events(self, date_from: Optional[str] = None) -> list[dict[str, Any]]:
        if date_from:
            sql = """
            SELECT id, title, event_date, start_time, end_time, category, fixed
            FROM src_calendar_events
            WHERE (fixed = 1 OR category IN ('medical', 'doctor', 'dentist', 'flight'))
              AND event_date >= ?
            ORDER BY event_date ASC, start_time ASC;
            """
            return self.execute_query(sql, (date_from,))
        else:
            sql = """
            SELECT id, title, event_date, start_time, end_time, category, fixed
            FROM src_calendar_events
            WHERE fixed = 1 OR category IN ('medical', 'doctor', 'dentist', 'flight')
            ORDER BY event_date ASC, start_time ASC;
            """
            return self.execute_query(sql)

    def query_calendar_busy_summary(self, event_date: str) -> dict[str, Any]:
        events = self.query_calendar_events_by_date(event_date)
        total_busy_minutes = 0
        for ev in events:
            s_parts = [int(p) for p in ev["start_time"].split(":")]
            e_parts = [int(p) for p in ev["end_time"].split(":")]
            dur = (e_parts[0] * 60 + e_parts[1]) - (s_parts[0] * 60 + s_parts[1])
            if dur > 0:
                total_busy_minutes += dur
        return {
            "date": event_date,
            "events_count": len(events),
            "total_busy_minutes": total_busy_minutes,
            "busy_hours": round(total_busy_minutes / 60.0, 1),
        }

    # --- Source 2: Task Backlog ---
    def query_urgent_backlog_tasks(self) -> list[dict[str, Any]]:
        sql = """
        SELECT task_id, title, estimated_minutes, priority, due_date, category, status
        FROM src_task_backlog
        WHERE priority IN ('urgent', 'high') AND status != 'done'
        ORDER BY CASE priority WHEN 'urgent' THEN 1 ELSE 2 END, due_date ASC;
        """
        return self.execute_query(sql)

    def query_tasks_by_due_date(self, target_date: str) -> list[dict[str, Any]]:
        sql = """
        SELECT task_id, title, estimated_minutes, priority, due_date, status, context_tags
        FROM src_task_backlog
        WHERE due_date <= ? AND status != 'done'
        ORDER BY due_date ASC, priority DESC;
        """
        return self.execute_query(sql, (target_date,))

    def query_tasks_by_category(self, category: str) -> list[dict[str, Any]]:
        sql = """
        SELECT task_id, title, estimated_minutes, priority, due_date, category, status
        FROM src_task_backlog
        WHERE category = ? AND status != 'done';
        """
        return self.execute_query(sql, (category,))

    # --- Source 3: User Preferences ---
    def query_user_work_parameters(self, user_id: str = "user_default") -> dict[str, Any]:
        sql = """
        SELECT user_id, name, work_start_time, work_end_time, min_buffer_minutes,
               focus_window_start, focus_window_end, lunch_window_start, lunch_window_end
        FROM src_user_preferences
        WHERE user_id = ?;
        """
        rows = self.execute_query(sql, (user_id,))
        return rows[0] if rows else {}

    def query_protected_categories(self, user_id: str = "user_default") -> list[str]:
        sql = "SELECT protected_categories FROM src_user_preferences WHERE user_id = ?;"
        rows = self.execute_query(sql, (user_id,))
        if rows and rows[0].get("protected_categories"):
            return [c.strip() for c in rows[0]["protected_categories"].split(",")]
        return ["medical", "doctor", "dentist", "flight"]

    # =========================================================================
    # ACTIVE USL CROSS-SOURCE QUERIES (2-3 Multi-Source Unified Queries)
    # =========================================================================
    def query_unified_schedule_with_buffers(self, target_date: str) -> list[dict[str, Any]]:
        """USL Active Query 1: Cross-joins events with user preferences,
        calculating duration, meeting buffer requirements, and immutability flags."""
        sql = """
        SELECT 
            e.id,
            e.title,
            e.event_date,
            e.start_time,
            e.end_time,
            e.priority,
            e.category,
            e.fixed,
            e.mobility,
            e.status,
            u.min_buffer_minutes,
            CASE 
                WHEN e.category IN ('medical', 'doctor', 'dentist', 'flight') THEN 1 
                WHEN e.fixed = 1 THEN 1
                ELSE 0 
            END AS is_immutable
        FROM src_calendar_events e
        CROSS JOIN src_user_preferences u
        WHERE e.event_date = ?
        ORDER BY e.start_time ASC;
        """
        return self.execute_query(sql, (target_date,))

    def query_backlog_calendar_feasibility(self, target_date: str) -> list[dict[str, Any]]:
        """USL Active Query 2: Evaluates backlog task urgency against day's capacity."""
        events = self.query_calendar_events_by_date(target_date)
        work_params = self.query_user_work_parameters()
        
        work_start = work_params.get("work_start_time", "08:30")
        work_end = work_params.get("work_end_time", "18:30")
        
        s_h, s_m = [int(p) for p in work_start.split(":")]
        e_h, e_m = [int(p) for p in work_end.split(":")]
        total_day_work_minutes = (e_h * 60 + e_m) - (s_h * 60 + s_m)
        
        busy_minutes = 0
        for ev in events:
            ev_s = [int(p) for p in ev["start_time"].split(":")]
            ev_e = [int(p) for p in ev["end_time"].split(":")]
            busy_minutes += (ev_e[0] * 60 + ev_e[1]) - (ev_s[0] * 60 + ev_s[1])
            
        free_minutes = max(0, total_day_work_minutes - busy_minutes)
        urgent_tasks = self.query_urgent_backlog_tasks()
        
        feasibility_report = []
        for t in urgent_tasks:
            est = int(t.get("estimated_minutes", 60))
            is_feasible = free_minutes >= est
            feasibility_report.append({
                "task_id": t["task_id"],
                "title": t["title"],
                "estimated_minutes": est,
                "priority": t["priority"],
                "due_date": t["due_date"],
                "target_date_free_minutes": free_minutes,
                "feasibility": "FEASIBLE" if is_feasible else "NEEDS_OPTIMIZATION",
            })
        return feasibility_report

    def find_free_focus_slots(self, target_date: str, required_minutes: int = 60) -> list[dict[str, str]]:
        """USL Active Query 3: Finds free focus slots in calendar respecting user buffer rules."""
        work_params = self.query_user_work_parameters()
        buffer_min = int(work_params.get("min_buffer_minutes", 15))
        work_start_m = 8 * 60 + 30
        work_end_m = 18 * 60 + 30
        
        events = self.query_calendar_events_by_date(target_date)
        busy_intervals = []
        for ev in events:
            s_h, s_m = [int(p) for p in ev["start_time"].split(":")]
            e_h, e_m = [int(p) for p in ev["end_time"].split(":")]
            # Apply buffer before and after meetings
            start_m = max(work_start_m, s_h * 60 + s_m - (buffer_min if ev.get("category") == "meeting" else 0))
            end_m = min(work_end_m, e_h * 60 + e_m + (buffer_min if ev.get("category") == "meeting" else 0))
            busy_intervals.append((start_m, end_m))
            
        busy_intervals.sort()
        
        free_slots = []
        cursor = work_start_m
        for b_start, b_end in busy_intervals:
            if b_start > cursor and (b_start - cursor) >= required_minutes:
                free_slots.append({
                    "start": f"{cursor // 60:02d}:{cursor % 60:02d}",
                    "end": f"{(cursor + required_minutes) // 60:02d}:{(cursor + required_minutes) % 60:02d}",
                    "available_minutes": str(b_start - cursor),
                })
            cursor = max(cursor, b_end)
            
        if work_end_m > cursor and (work_end_m - cursor) >= required_minutes:
            free_slots.append({
                "start": f"{cursor // 60:02d}:{cursor % 60:02d}",
                "end": f"{(cursor + required_minutes) // 60:02d}:{(cursor + required_minutes) % 60:02d}",
                "available_minutes": str(work_end_m - cursor),
            })
            
        return free_slots

    # =========================================================================
    # DATA QUALITY RULES (Executed by Zetaris USL Engine)
    # =========================================================================
    def execute_data_quality_rules(self) -> dict[str, Any]:
        """Execute automated Data Quality Rules over the semantic layer.
        
        Rules verified:
          1. RULE_TIME_ORDER: start_time must strictly precede end_time.
          2. RULE_NO_OVERLAPPING_PINNED: Pinned/medical events must never overlap.
          3. RULE_VALID_PRIORITY: Priorities must be one of urgent, high, medium, low.
          4. RULE_NON_EMPTY_IDENTIFIERS: All events and tasks must have non-empty titles.
        """
        results = {
            "all_passed": True,
            "total_rules": 4,
            "rules_passed": 0,
            "violations": [],
        }

        # Rule 1: Time order check
        r1_sql = """
        SELECT id, title, event_date, start_time, end_time 
        FROM src_calendar_events 
        WHERE start_time >= end_time;
        """
        r1_violations = self.execute_query(r1_sql)
        if r1_violations:
            results["all_passed"] = False
            results["violations"].append({
                "rule": "RULE_TIME_ORDER",
                "severity": "CRITICAL",
                "message": f"Found {len(r1_violations)} events where start_time >= end_time",
                "entities": r1_violations,
            })
        else:
            results["rules_passed"] += 1

        # Rule 2: Overlapping pinned events check
        r2_sql = """
        SELECT a.id as id_a, a.title as title_a, b.id as id_b, b.title as title_b, a.event_date
        FROM src_calendar_events a
        JOIN src_calendar_events b 
          ON a.event_date = b.event_date 
         AND a.id < b.id
         AND (a.fixed = 1 OR a.category IN ('medical', 'doctor', 'dentist'))
         AND (b.fixed = 1 OR b.category IN ('medical', 'doctor', 'dentist'))
         AND (a.start_time < b.end_time AND a.end_time > b.start_time);
        """
        r2_violations = self.execute_query(r2_sql)
        if r2_violations:
            results["all_passed"] = False
            results["violations"].append({
                "rule": "RULE_NO_OVERLAPPING_PINNED",
                "severity": "CRITICAL",
                "message": f"Found {len(r2_violations)} overlapping pinned/medical events",
                "entities": r2_violations,
            })
        else:
            results["rules_passed"] += 1

        # Rule 3: Valid priority check
        r3_sql = """
        SELECT task_id, title, priority 
        FROM src_task_backlog 
        WHERE priority NOT IN ('urgent', 'high', 'medium', 'low');
        """
        r3_violations = self.execute_query(r3_sql)
        if r3_violations:
            results["all_passed"] = False
            results["violations"].append({
                "rule": "RULE_VALID_PRIORITY",
                "severity": "WARNING",
                "message": f"Found {len(r3_violations)} tasks with invalid priority scale",
                "entities": r3_violations,
            })
        else:
            results["rules_passed"] += 1

        # Rule 4: Non-empty titles
        r4_sql = """
        SELECT id, event_date FROM src_calendar_events WHERE trim(title) = '';
        """
        r4_violations = self.execute_query(r4_sql)
        if r4_violations:
            results["all_passed"] = False
            results["violations"].append({
                "rule": "RULE_NON_EMPTY_IDENTIFIERS",
                "severity": "WARNING",
                "message": f"Found {len(r4_violations)} events with empty titles",
                "entities": r4_violations,
            })
        else:
            results["rules_passed"] += 1

        return results

    # =========================================================================
    # EVENT PERSISTENCE HELPER
    # =========================================================================
    def persist_calendar_event(self, event_dict: dict[str, Any]) -> None:
        """Persist or update an event in SQLite USL and synchronize JSON storage."""
        ev_id = str(event_dict.get("id"))
        with self._db:
            self._db.execute(
                """
                INSERT OR REPLACE INTO src_calendar_events 
                (id, title, event_date, start_time, end_time, priority, category, description, fixed, mobility, status, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ev_id,
                    str(event_dict.get("title", "")),
                    str(event_dict.get("date", "")),
                    str(event_dict.get("start", "")),
                    str(event_dict.get("end", "")),
                    str(event_dict.get("priority", "medium")),
                    str(event_dict.get("category", "task")),
                    str(event_dict.get("description", "")),
                    bool(event_dict.get("fixed", False)),
                    str(event_dict.get("mobility", "movable")),
                    str(event_dict.get("status", "planned")),
                    str(event_dict.get("source", "agent")),
                ),
            )
