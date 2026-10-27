# TimePilot AI — Video Recording Script (Super Simple Teleprompter)

> **Total Time:** ~2 minutes  
> **How to use:** Read ONLY the text inside the **"🎙️ READ OUT LOUD"** blocks.  
> Every sentence is short and easy to speak!

---

## 🟢 PART 1: INTRO (0:00 – 0:30)

### 🖥️ WHAT TO SHOW ON SCREEN:
- Open your browser at `http://localhost:8000`.
- Show the clean calendar screen.

### 🎙️ READ OUT LOUD:
> "Hi everyone!  
> I am excited to show you **TimePilot AI**.  
>  
> This is an AI calendar agent that does real work.  
> We built it for the **Reasoning Architecture** track.  
>  
> Why did we build this?  
> Because managing your calendar is hard.  
> You have meetings in your calendar.  
> You have urgent tasks in Jira.  
> And regular AI chatbots are not helpful. They just make things up and break your schedule.  
>  
> TimePilot fixes that."

---

## 🟢 PART 2: LIVE DEMO (0:30 – 1:15)

### 🖥️ WHAT TO SHOW ON SCREEN:
- Click the chat box.
- Type: `Urgent: schedule security audit at 2 PM for 45 minutes`
- Press Enter.
- Watch 3:00 PM get scheduled, and watch UI Prototyping move to 3:45 PM.
- Click on the task to open the "Explain Why" box.

### 🎙️ READ OUT LOUD:
> "Let's see a live demo.  
>  
> I will type:  
> *'Urgent: schedule security audit at 2 PM for 45 minutes'*.  
>  
> Look at the calendar.  
> 2 PM is already busy with our Team Sync meeting!  
>  
> A regular chatbot would just make a mistake or double-book.  
> But TimePilot is smarter.  
>  
> Our Critic agent checks the rules and says: *'No, 2 PM is blocked.'*  
>  
> So it finds a new slot at 3 PM.  
> And it moves our flexible design task to 3:45 PM.  
>  
> If I click the task, look here:  
> TimePilot explains **WHY** it made this choice.  
> Everything is clear and verified."

---

## 🟢 PART 3: AGENTS & TRACES (1:15 – 1:45)

### 🖥️ WHAT TO SHOW ON SCREEN:
- Switch to your terminal showing `tail -f logs/agent_traces.jsonl` (or the Traces panel in the UI).
- Point to the agent names and the model names.

### 🎙️ READ OUT LOUD:
> "Now let's look at the traces under the hood.  
>  
> This is a real 4-agent team:  
> 1. **Planner Agent** finds the urgent goal.  
> 2. **Context Agent** gets schedule data from Zetaris.  
> 3. **Conflict Critic** checks constraints and rejects bad slots.  
> 4. And **Reconciler Agent** saves the final plan.  
>  
> Every step runs on real **NVIDIA Nemotron** models through **Meterless**."

---

## 🟢 PART 4: SPONSORS (1:45 – 2:15)

### 🖥️ WHAT TO SHOW ON SCREEN:
- Run `python3 -m unittest discover tests` in the terminal.
- Show that all 101 tests pass!

### 🎙️ READ OUT LOUD:
> "All sponsor tools do real work here:  
>  
> **Zetaris** is our data layer. It connects calendar events, task backlogs, and buffer rules in one place.  
>  
> **Meterless** gives our agent memory, so it learns user habits over time.  
>  
> **NVIDIA** powers our intelligence with Nemotron models.  
>  
> And we used **Cursor** as our coding tool."

---

## 🟢 PART 5: FINISH (2:15 – 2:30)

### 🖥️ WHAT TO SHOW ON SCREEN:
- Show your GitHub repo or the calendar.

### 🎙️ READ OUT LOUD:
> "Judges can run this project in one command with Docker, or in Sample Mode without any API keys.  
>  
> All 101 tests pass.  
>  
> Our code is 100% public on GitHub.  
> Thank you for watching!"
