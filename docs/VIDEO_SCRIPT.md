# TimePilot AI — Demo Video Recording Script

> **Hackathon:** Open Agent Hackathon 2026  
> **Track:** Track 03: Reasoning Architecture  
> **Target Video Duration:** 2:30 – 3:30 minutes (Limit: 1 to 4 minutes max)  
> **Key Goal:** 15/15 Demo Points + 10/10 Sponsor Tech Points. Show the agent doing real work live on screen.

---

## ⚠️ Pre-Recording Safety Checklist
- [ ] No API keys, passwords, or tokens displayed on screen (check terminal commands and `.env`).
- [ ] Backend running (`python run.py --serve --port 8000`) or Docker active.
- [ ] Browser open at `http://localhost:8000` in full screen or clean window.
- [ ] Terminal split ready to show `tail -f logs/agent_traces.jsonl`.
- [ ] Audio/Mic checked and clean.

---

## 🎬 Scene-by-Scene Script

### Scene 1: Introduction & Problem (0:00 – 0:35)

| Time | What to Show on Screen | Spoken Script (Russian) | Spoken Script (English) |
|---|---|---|---|
| **0:00 – 0:15** | Open the TimePilot AI Web UI (`http://localhost:8000`). Show the clean dark-mode schedule grid with existing meetings and tasks. | «Всем привет! Это **TimePilot AI** — автономный когнитивный календарный агент, созданный для трека **Reasoning Architecture** на Open Agent Hackathon 2026. Наш девиз: *Не очередной чат-бот, а агент, который делает реальную работу*.» | "Hello everyone! This is **TimePilot AI** — an autonomous cognitive scheduling agent built for the **Reasoning Architecture** track at Open Agent Hackathon 2026. Our mission: *Not another chatbot, an agent that does real work.*" |
| **0:15 – 0:35** | Hover over calendar blocks: show a pinned doctor visit, a team sync, and backlog tasks on the right. | «Главная проблема современных календарей — фрагментация данных. Срочные баги пылятся в бэклоге Jira, календари слепы к буферам встреч, а простые LLM-боты ломают расписание и не могут объяснить свои действия. TimePilot AI решает это через связку **Zetaris USL**, памяти **Meterless H-MEM** и архитектуры с активной критикой.» | "Today's scheduling is broken by fragmented data silos. Urgent issues sit unlinked in Jira backlogs, calendars ignore meeting buffers, and standard LLMs hallucinate slots. TimePilot AI unifies data via **Zetaris USL**, cognitive memory via **Meterless H-MEM**, and a self-correcting multi-agent loop." |

---

### Scene 2: Live Reasoning Demo — Conflict & Self-Correction (0:35 – 1:30)

| Time | What to Show on Screen | Spoken Script (Russian) | Spoken Script (English) |
|---|---|---|---|
| **0:35 – 0:55** | Type in chat input or click voice mic: *"Срочно добавь аудит утечки токенов на 14:00 на 45 минут"*. Hit Enter. | «Давайте проверим агента в деле. Я отправляю критический запрос: *«Срочно добавь аудит утечки токенов на 14:00 на 45 минут»*. Но в 14:00 в календаре уже стоит важный Team Sync!» | "Let's test the agent live. I submit a high-priority request: *'Urgent: schedule security token leak audit at 14:00 for 45 minutes'*. But 14:00 collides with a pinned Team Sync meeting!" |
| **0:55 – 1:30** | Watch the schedule update in real time: The urgent audit is placed at 15:00–15:45, and the movable "UI Prototyping" task is shifted from 15:30 to 15:45. Click the event to open **"Explain Why"**. | «Посмотрите на результат! Вместо тупого наложения агент запустил 4-агентный цикл. **ConflictCritic** отклонил слот на 14:00 из-за коллизии с синк-встречей, отправил запрос на доработку, а **ContextAgent** определил гибкие задачи. В итоге аудит встал на 15:00, а сессия прототипирования сдвинута на 15:45. А в окне **Explain Why** видна полная цепочка доказательств без галлюцинаций.» | "Look at the result! Instead of a naive overwrite, TimePilot executed a 4-agent loop. **ConflictCritic** rejected the 14:00 slot, triggered a retry branch, identified flexible tasks, scheduled the audit at 15:00, and shifted movable UI prototyping to 15:45. The **Explain Why** drawer shows the complete evidence justification." |

---

### Scene 3: Live Traces & Multi-Agent Critique Loop (1:30 – 2:15)

| Time | What to Show on Screen | Spoken Script (Russian) | Spoken Script (English) |
|---|---|---|---|
| **1:30 – 1:55** | Switch to the Terminal window showing `logs/agent_traces.jsonl` or expand the UI Traces drawer. | «А теперь заглянем под капот в живые трейсы. Это не линейный пайплайн A->B->C. Мы видим: 1) **PlannerAgent** классифицирует интент через Scout Intent; 2) **ContextAgent** запрашивает данные из Zetaris USL; 3) **ConflictCritic** отклоняет слот со статусом `needs_revision`! 4) Запускается retry_count=1 с новыми ограничениями; 5) И только после валидации **ReconcilerAgent** утверждает план.» | "Now let's inspect the live traces under the hood. This is NOT a linear pipeline. We see: 1) **PlannerAgent** decomposes intent via Scout Intent; 2) **ContextAgent** queries Zetaris USL; 3) **ConflictCritic** actively rejects the proposal with `needs_revision`! 4) A retry branch executes (`retry_count=1`); 5) **ReconcilerAgent** commits the verified plan." |
| **1:55 – 2:15** | Highlight the model names in the logs: `nvidia/nemotron-3-super-120b-a12b` and `nvidia/nemotron-3.5-lightning-30b-a3b`. | «Обратите внимание: каждое действие логирует конкретную модель NVIDIA. Глубокое планирование выполняет **Nemotron-3 Super 120B**, а быструю критику ограничений — легковесный **Nemotron-3.5 Lightning 30B** через Meterless Nightshift.» | "Notice that every turn logs the exact NVIDIA model. Deep planning runs on **Nemotron-3 Super 120B**, while fast constraint critiques run on **Nemotron-3.5 Lightning 30B** through Meterless Nightshift." |

---

### Scene 4: Sponsor Tech Highlights & Zetaris USL (2:15 – 2:55)

| Time | What to Show on Screen | Spoken Script (Russian) | Spoken Script (English) |
|---|---|---|---|
| **2:15 – 2:35** | Show `data/zetaris_usl_ddl.sql` or run the test `python tests/test_zetaris_usl.py`. | «Как интегрированы технологии спонсоров: **Zetaris** является фундаментальным слоем данных. Мы объединили 3 источника: календарь, бэклог задач и правила буферов. Расчет доступных окон вынесен прямо в SQL-представления USL, а перед записью проверяются 4 правила качества данных (Data Quality Rules).» | "How sponsor tech is integrated: **Zetaris** serves as our data layer. We federated 3 sources: calendar events, task backlog, and buffer preferences. Feasibility joins run directly inside Zetaris SQL views, guarded by 4 automated Data Quality rules." |
| **2:35 – 2:55** | Run the meterless test: `python tests/test_meterless_engine.py` and show 101 tests passing. | «В **Meterless** мы реализовали движок **H-MEM** с трехуровневой памятью — рабочей, эпизодической и долговременной, где сохраняются привычки пользователя, и движок **Scout Intent**. А для среды разработки мы использовали **Cursor с поддержкой Space XAI**.» | "With **Meterless**, we implemented the **H-MEM** hierarchical memory engine (working, episodic, and long-term habits) and the **Scout Intent** engine. For development, we built everything inside **Cursor with Space XAI**." |

---

### Scene 5: Programmatic Driving & Conclusion (2:55 – 3:20)

| Time | What to Show on Screen | Spoken Script (Russian) | Spoken Script (English) |
|---|---|---|---|
| **2:55 – 3:15** | Run `curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d @input_examples/example_1.json` or show `SAMPLE_MODE=true`. | «Судьи могут запустить проект одной командой: через Docker, через REST endpoint `POST /run`, или в автономном режиме `SAMPLE_MODE=true` без внешних ключей. Все 101 тест проходят безупречно.» | "Judges can drive TimePilot programmatically with a single command via Docker, `POST /run`, or with `SAMPLE_MODE=true` without external credentials. All 101 automated tests pass cleanly." |
| **3:15 – 3:30** | Back to the UI showing the final clean calendar state. | «TimePilot AI превращает календарный хаос в надежное, предсказуемое расписание. Спасибо за внимание, репозиторий открыт на GitHub!» | "TimePilot AI turns calendar chaos into reliable, autonomous scheduling. Thank you, and explore our open repository on GitHub!" |

---

## 🎙️ Recording Tips for Top Score:
1. **Pacing:** Speak clearly and with energy; 2 minutes 45 seconds is the sweet spot.
2. **Screen layout:** Keep the browser on 70% of the screen and a sleek terminal on 30% showing the trace logs in real-time.
3. **No credentials:** Double check that no tokens or passwords appear in your terminal history or URL bar.
4. **Link check:** When uploading to YouTube/Drive, verify the link in an Incognito/Private window before submitting to HackOS!
