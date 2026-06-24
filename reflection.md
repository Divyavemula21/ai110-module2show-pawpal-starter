# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?


For the initial architecture of PawPal+, I designed a top-down hierarchical structure composed of four main classes to cleanly separate data management from scheduling logic. The system fulfills three core user actions: entering profile information, managing individual care tasks, and generating an optimized daily schedule.

The core classes and their initial responsibilities include:
1. **Owner**: Acts as the root profile manager. Its primary responsibility is maintaining ownership of multiple pets via a collection (`List[Pet]`), serving as the primary entry point for user-specific data like `name` and general care preferences.
2. **Pet**: Represents an individual animal profile. It stores unique traits (name, type, age) and acts as the data container for that pet's individual needs by managing its own isolated list of care tasks.
3. **CareTask**: A cleanly structured data object (utilizing Python Dataclasses) that holds granular details about an individual activity—such as timing (`due_time`), duration in minutes, importance (`priority`), and recurrence (`frequency`). It includes methods to modify details or toggle completion status.
4. **Scheduler (ScheduleManager)**: The operational "brain" of the application. It is completely decoupled from data persistence; instead, it accepts an `Owner` instance on initialization and dynamically aggregates, sorts, filters, and analyzes tasks down the ownership tree to generate a chronological plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Following an architecture review of the initial skeleton, the following enhancements were implemented to prevent downstream logic bottlenecks and accommodate upcoming features:
* **Tightened Method Signatures**: Adjusted `Scheduler.filter_tasks` arguments to accept `Optional` parameters, ensuring the user interface can query tasks generically or drill down specifically by pet name or completion state.
* **Granular Time Metric**: Explicitly named the duration field `duration_mins` rather than a generic `duration` integer to ensure absolute clarity across the codebase when managing scheduling constraints.
* **Uncoupled Metadata**: Removed hardcoded time allocation dependencies (like `available_hours`) directly inside the `Owner` class, moving all temporal and analytical calculations completely into the `Scheduler` to preserve a strict single-responsibility design.

1. Enter Profile Information: A user can input basic details about themselves as the owner and about their pet (e.g., name, breed, or age) to customize the application context.

2. Manage Care Tasks: A user can add, edit, or track specific pet care activities—such as walks, feeding, medications, enrichment, or grooming—while assigning constraints like task duration and priority levels.

3. Generate and View a Daily Schedule: A user can trigger the application to evaluate their constraints (such as available time or priority) and output a clear, chronologically organized daily plan that explains the reasoning behind the schedule.

- Owner
Represents the user of the application.

Attributes:

name (String): The owner's name.

available_hours (Float): Total hours the owner has available in a day for pet care.

preferences (List/Dict): Any specific choices (e.g., preferred walking times).

Methods:

update_profile(name, available_hours): Updates the owner's information.

- Pet
Represents the pet receiving care.

Attributes:

name (String): The pet's name.

pet_type (String): e.g., Dog, Cat, Golden Retriever.

age (Integer/Float): The pet's age.

Methods:

get_profile_summary(): Returns a formatted string summarizing the pet's details.

- CareTask
Represents an individual activity or task that needs to be scheduled.

Attributes:

title (String): Name of the task (e.g., "Morning Walk", "Feeding").

duration (Integer): Time required to complete the task in minutes.

priority (String/Integer): Importance level (e.g., "High", "Medium", "Low" or 1-3).

is_completed (Boolean): Tracks whether the task was done.

Methods:

update_task_details(duration, priority): Modifies constraints on the task.

toggle_complete(): Marks the task as completed or incomplete.

- ScheduleManager (or Scheduler)
The engine responsible for handling the collection of tasks and optimizing the plan.

Attributes:

tasks (List of CareTask objects): The master list of all entered tasks.

daily_plan (List of CareTask objects): The filtered, sorted, and scheduled list for the day.

Methods:

add_task(task) / remove_task(task_id): Manages the collection of tasks.

generate_daily_schedule(available_minutes): Sorts tasks (e.g., by priority or duration), filters out tasks that exceed the available time constraint, and populates daily_plan.

get_schedule_explanation(): Generates a natural language string explaining the logic behind why certain tasks were prioritized or cut.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
