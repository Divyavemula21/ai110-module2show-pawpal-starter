# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Owner: Jordan  (available today: 90 min)
Pets:
  - Mochi (dog, age 3)  [2 task(s)]
  - Biscuit (cat, age 5)  [2 task(s)]

================================================
Today's Schedule
================================================
Daily plan (chosen by priority, then shortest first):
  08:00  Biscuit — Feeding (10 min) [priority: high, daily]
  08:10  Mochi — Morning walk (30 min) [priority: high, daily]
  08:40  Biscuit — Litter clean (15 min) [priority: medium, daily]

Not scheduled (ran out of time or lower priority):
  - Mochi — Grooming (45 min) [low]



## Smarter Scheduling Features

PawPal+ uses an intelligent scheduling layer built into the `ScheduleManager` class to optimize a pet owner's day:


| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting |ScheduleManager.generate_daily_schedule()
ScheduleManager.sort_by_time() | Sorts items chronologically for the timeline view, or optimizes greedily by priority (highest first) and duration (shortest first) to maximize your time budget. |
| Filtering | ScheduleManager.filter_tasks()| Skips tasks that do not fit within the owner's remaining available hours and splits out omitted items. Also allows filtering by pet name.|
| Conflict handling | ScheduleManager.check_conflicts()| Utilizes an optimized tracking hash-map to flag overlapping tasks scheduled for the exact same date and time. |
| Recurring tasks | cheduleManager.complete_task_and_recur()| Automatically calculates the next due date (+1 day for daily, +7 days for weekly) and appends a fresh tracking placeholder.|

## 📸 Demo Walkthrough

To interact with the application, launch the UI using streamlit run app.py and try this example flow:

Configure Owner Profile: In the 👤 Owner panel, change the name and update your available hours (e.g., set to 4.0 hours). Click Save owner.

Register a Pet: In the 🐕 Add a pet section, add a pet name (e.g., "Mochi"), select its species, enter its age, and click Add pet.

Schedule Tasks: Under 📋 Add a task, pick your pet, enter a task description (e.g., "Morning Walk"), set the duration to 30, pick a priority level, and click Schedule Task. Add a second task at the exact same time slot to watch the system catch a conflict!

Generate the Schedule: Scroll to 🗓️ Build Schedule and click Generate schedule. The app will automatically output your optimized day list or print active system warnings if there are scheduling conflicts


## 🧪 Testing PawPal+

```bash
# Run the full test suite:

python -m pytest -v

# Run with coverage:
pytest --cov
```

Sample test output:


# pytest output here

============================= test session starts ==============================
collected 5 items

tests/test_pawpal.py::test_task_completion_changes_status PASSED          [ 20%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED    [ 40%]
tests/test_pawpal.py::test_task_sorting_chronological PASSED              [ 60%]
tests/test_pawpal.py::test_recurrence_logic PASSED                        [ 80%]
tests/test_pawpal.py::test_conflict_detection PASSED                      [100%]

============================== 5 passed in 0.08s ===============================

Confidence Level: ⭐⭐⭐⭐⭐ (5/5 stars)

# Project Structure

```
PawPal+
│
├── app.py
├── pawpal_system.py
├── main.py
├── tests
│   └── test_pawpal.py
├── diagrams
│   └── uml_final.mmd
├── README.md
└── reflection.md
```

---

# Technologies Used

- Python
- Streamlit
- Dataclasses
- Pytest

---

# Future Improvements

- Calendar view
- Email reminders
- Notifications
- Drag-and-drop scheduling
- Mobile-friendly interface
- Database support

---

# Author

Divyasree Vemula