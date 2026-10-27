# TimePilot AI — Simple Demo Video Script (Easy English)

> **Duration:** ~2.5 minutes (Target: between 1 and 4 minutes)  
> **Style:** Natural, conversational, clear, simple English without complex jargon.  
> **Key goal:** 15/15 Demo points + 10/10 Sponsor Tech points.

---

## 🎬 Step-by-Step Recording Guide

### 1. Introduction (0:00 – 0:30)
* **On Screen:** Open the TimePilot AI calendar (`http://localhost:8000`). Show the clean schedule grid with existing meetings and tasks.
* **What to Say:**
  > *"Hi everyone! This is **TimePilot AI** — an autonomous AI calendar agent built for the **Reasoning Architecture** track at the Open Agent Hackathon 2026.*  
  >  
  > *Our mission is simple: **Not another chatbot, but an agent that does real work.***  
  >  
  > *Today, scheduling is messy. Urgent tasks sit forgotten in Jira backlogs, calendars ignore meeting buffers, and standard AI chatbots don't really help — they hallucinate free slots and break our schedules. TimePilot AI fixes this."*

---

### 2. Live Demo: Resolving a Real Conflict (0:30 – 1:20)
* **On Screen:** Type in the chat box:  
  `Urgent: schedule security token leak audit at 2 PM for 45 minutes`  
  and press Enter.
* **What to Show:**
  - Notice that 2:00 PM is already busy with an important **Team Project Sync**.
  - Show TimePilot placing the urgent audit at **3:00 PM – 3:45 PM**.
  - Show the flexible **UI Prototyping** task moving automatically from **3:30 PM to 3:45 PM**.
  - Click on the event card to open the **Explain Why** drawer.
* **What to Say:**
  > *"Let me show you a real example.*  
  >  
  > *I type: 'Urgent: schedule security token leak audit at 2 PM for 45 minutes'.*  
  >  
  > *Notice that 2 PM is already booked for our Team Sync meeting!*  
  >  
  > *Instead of breaking the calendar or showing an error, TimePilot reasons through the problem. The **Conflict Critic** agent sees the collision and says 'no'.*  
  >  
  > *Then, the agent checks which tasks are flexible. It finds an open slot at 3 PM for our urgent audit, and automatically moves our flexible UI session by 15 minutes.*  
  >  
  > *If I click on the task, the **Explain Why** window shows the full evidence behind this decision."*

---

### 3. Agent Traces & Reasoning Architecture (1:20 – 1:55)
* **On Screen:** Switch to the terminal showing `logs/agent_traces.jsonl` or expand the live Traces panel.
* **What to Show:** Point out the steps:
  - `PlannerAgent` (finds urgency)
  - `ContextAgent` (reads schedule)
  - `ConflictCritic` (gives a red/yellow warning and triggers retry)
  - `ReconcilerAgent` (approves final plan)
  - NVIDIA Nemotron model names in the logs.
* **What to Say:**
  > *"Now, let's look at the live traces.*  
  >  
  > *This is not a simple linear chain. It is an active 4-agent loop:*  
  > *- **Planner Agent** checks user intent and urgency.*  
  > *- **Context Agent** pulls schedule data from Zetaris.*  
  > *- **Conflict Critic** tests constraints, rejects bad slots, and asks for a retry.*  
  > *- And **Reconciler Agent** saves the verified plan.*  
  >  
  > *You can see every step logs the exact NVIDIA model doing the work: **Nemotron 3 Super** for deep planning, and **Nemotron 3.5 Lightning** for fast checks."*

---

### 4. Sponsor Technologies (1:55 – 2:30)
* **On Screen:** Run `python3 -m unittest discover tests` in terminal (101 tests pass) and show `data/zetaris_usl_ddl.sql`.
* **What to Say:**
  > *"All sponsor tools do real, necessary work:*  
  > *- **Zetaris** is our data layer. It connects calendar events, Jira tasks, and user preferences into one clean layer with automated data quality checks.*  
  > *- **Meterless** gives our agent memory. The H-MEM engine remembers past decisions so the agent learns user habits over time.*  
  > *- **NVIDIA** powers our intelligence with Nemotron models and Riva voice recognition.*  
  > *- And we used **Cursor with SpaceX AI** as our IDE to build this system and write 101 automated unit tests."*

---

### 5. Conclusion (2:30 – 2:45)
* **On Screen:** Back to the clean calendar screen or show the GitHub repo.
* **What to Say:**
  > *"Judges can test TimePilot in one command using Docker, or in Sample Mode with zero setup.*  
  >  
  > *TimePilot turns calendar chaos into reliable, clear action. Our code is 100% public on GitHub. Thank you for watching!"*

---

## 💡 Quick Tips for Clear Speech:
1. Speak at a calm, relaxed pace.
2. Pause for 1 second between steps so the viewer can see the screen change.
3. Don't worry about sounding perfect — clear, simple sentences sound best!
