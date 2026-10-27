-- ============================================================================
-- Zetaris Unified Semantic Layer (USL) DDL
-- Project: TimePilot AI
-- Purpose: Unified semantics across Fragmented Calendar, Task Backlog, and User Context
-- ============================================================================

-- SOURCE 1: Calendar Schedule Source
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

-- SOURCE 2: Engineering & Task Backlog Source (Jira / Linear / Todoist)
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

-- SOURCE 3: User Context, Working Hours & Biological Energy Preferences
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

-- ============================================================================
-- UNIFIED SEMANTIC LAYER VIEWS (Active Cross-Source Semantic Models)
-- ============================================================================

-- USL VIEW 1: Unified Schedule & Availability View
-- Combines calendar events with normalized duration and boundary checks
CREATE VIEW IF NOT EXISTS usl_unified_schedule AS
SELECT 
    e.id AS event_id,
    e.title,
    e.event_date,
    e.start_time,
    e.end_time,
    (strftime('%s', '2000-01-01 ' || e.end_time) - strftime('%s', '2000-01-01 ' || e.start_time)) / 60 AS duration_minutes,
    e.priority,
    e.category,
    e.fixed,
    e.mobility,
    e.status,
    u.user_id,
    u.min_buffer_minutes,
    CASE 
        WHEN e.category IN ('medical', 'doctor', 'dentist', 'flight') THEN 1 
        WHEN e.fixed = 1 THEN 1
        ELSE 0 
    END AS is_immutable
FROM src_calendar_events e
CROSS JOIN src_user_preferences u;

-- USL VIEW 2: Backlog Urgency & Scheduling Readiness
-- Prioritizes tasks with upcoming due dates that need calendar slots
CREATE VIEW IF NOT EXISTS usl_urgent_backlog_tasks AS
SELECT 
    t.task_id,
    t.title,
    t.estimated_minutes,
    t.priority,
    t.due_date,
    t.category,
    t.status,
    CASE 
        WHEN t.priority = 'urgent' THEN 1
        WHEN t.priority = 'high' THEN 2
        WHEN t.priority = 'medium' THEN 3
        ELSE 4
    END AS priority_rank,
    u.user_id,
    u.focus_window_start,
    u.focus_window_end
FROM src_task_backlog t
CROSS JOIN src_user_preferences u
WHERE t.status != 'done';

-- USL VIEW 3: Cross-Source Schedule Feasibility & Allocation
-- Joins calendar commitments with backlog demands and preference buffer rules
CREATE VIEW IF NOT EXISTS usl_cross_source_feasibility AS
SELECT 
    b.task_id,
    b.title AS task_title,
    b.estimated_minutes,
    b.priority AS task_priority,
    b.due_date,
    s.event_date,
    COUNT(s.event_id) AS scheduled_events_count,
    SUM(s.duration_minutes) AS total_busy_minutes,
    ( (strftime('%s', '2000-01-01 ' || p.work_end_time) - strftime('%s', '2000-01-01 ' || p.work_start_time)) / 60 ) - COALESCE(SUM(s.duration_minutes), 0) AS remaining_free_minutes,
    CASE 
        WHEN ( (strftime('%s', '2000-01-01 ' || p.work_end_time) - strftime('%s', '2000-01-01 ' || p.work_start_time)) / 60 ) - COALESCE(SUM(s.duration_minutes), 0) >= b.estimated_minutes 
        THEN 'FEASIBLE'
        ELSE 'OVERCAPACITY'
    END AS fit_feasibility
FROM src_task_backlog b
CROSS JOIN src_user_preferences p
LEFT JOIN usl_unified_schedule s ON s.event_date = b.due_date
WHERE b.status = 'todo'
GROUP BY b.task_id, b.due_date;

-- ============================================================================
-- DATA QUALITY RULES (Executed by Zetaris USL Engine)
-- ============================================================================

-- Rule 1: Chronological Order (start_time < end_time)
-- Rule 2: Non-Overlapping Fixed/Protected Events on the same date
-- Rule 3: Valid Priority Categorization (urgent, high, medium, low)
-- Rule 4: Work Hours Boundary Alignment

