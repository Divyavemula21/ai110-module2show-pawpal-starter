"""PawPal+ core system.

Implements the four classes from the design:
    - CareTask        (Task)  : a single care activity
    - Pet                     : pet details + the list of tasks that belong to it
    - Owner                   : manages multiple pets, exposes all their tasks
    - ScheduleManager (Scheduler) : the "brain" that retrieves, organizes, and
                                    schedules tasks across all of the owner's pets

Plain data objects (CareTask, Pet, Owner) use @dataclass to stay clean and
boilerplate-free. ScheduleManager carries the cross-pet logic.

Ownership of tasks:
    Owner --> Pet --> CareTask
The scheduler does NOT own tasks; it pulls them from the pets at plan time.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Dict, Any, Optional

# Priority labels mapped to a sort weight (higher = more important).
PRIORITY_WEIGHT: Dict[str, int] = {"high": 3, "medium": 2, "low": 1}


@dataclass
class CareTask:
    """A single care activity.

    Captures: description (title), the time it takes, how often it recurs
    (frequency), and whether it's been done (completion status).
    """

    title: str                    # what the task is (its description)
    duration: int                 # the time it takes, in minutes (must be > 0)
    frequency: str = "daily"      # e.g. "daily", "weekly", "monthly"
    priority: str = "medium"      # "high" | "medium" | "low"
    is_completed: bool = False 
    due_date: date = field(default_factory=date.today)
    time: str = "08:00"           # format: "HH:MM"
    
    # Back-reference to the pet this task belongs to. Set by Pet.add_task().
    # repr/compare excluded to avoid Pet<->CareTask recursion and identity surprises.
    pet: Optional["Pet"] = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate the task's duration right after construction."""
        self._validate_duration(self.duration)

    @staticmethod
    def _validate_duration(duration: int) -> None:
        """Reject non-positive durations, which would corrupt the time budget."""
        if duration <= 0:
            raise ValueError(f"duration must be a positive number of minutes, got {duration}")

    def update_task_details(self, duration: int, priority: str) -> None:
        """Modify this task's time/priority constraints."""
        self._validate_duration(duration)
        self.duration = duration
        self.priority = priority

    def toggle_complete(self) -> None:
        """Flip the completed flag."""
        self.is_completed = not self.is_completed

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    @property
    def priority_weight(self) -> int:
        """Numeric weight for sorting; unknown labels sort lowest."""
        return PRIORITY_WEIGHT.get(self.priority.lower(), 0)


@dataclass
class Pet:
    """Pet details plus the list of care tasks that belong to this pet."""

    name: str
    pet_type: str = "other"
    age: int = 0
    tasks: List[CareTask] = field(default_factory=list)

    def get_profile_summary(self) -> str:
        """Return a short, readable summary of the pet."""
        return f"{self.name} ({self.pet_type}, age {self.age})"

    def add_task(self, task: CareTask) -> None:
        """Attach a task to this pet, recording the back-reference."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove every task on this pet matching the given title."""
        self.tasks = [t for t in self.tasks if t.title != title]


@dataclass
class Owner:
    """Manages multiple pets and provides access to all of their tasks."""

    name: str
    available_hours: float = 0.0
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)
    schedule: Optional["ScheduleManager"] = None  # set in __post_init__

    def __post_init__(self) -> None:
        """Give the owner their own scheduler if one wasn't supplied."""
        if self.schedule is None:
            self.schedule = ScheduleManager()

    def add_pet(self, pet: Pet) -> None:
        """Register a pet this owner cares for."""
        self.pets.append(pet)

    def all_tasks(self) -> List[CareTask]:
        """Every task across every pet, flattened into one list."""
        return [task for pet in self.pets for task in pet.tasks]

    def update_profile(self, name: str, available_hours: float) -> None:
        """Update the owner's basic info."""
        self.name = name
        self.available_hours = available_hours

    @property
    def available_minutes(self) -> int:
        """Available time expressed in minutes (what the scheduler uses)."""
        return int(self.available_hours * 60)


@dataclass
class ScheduleManager:
    """The brain: retrieves, organizes, and schedules tasks across pets."""

    daily_plan: List[CareTask] = field(default_factory=list)
    # Incomplete tasks considered in the most recent run (for the explanation).
    _considered: List[CareTask] = field(default_factory=list, repr=False)
    # Cache detected warnings from the latest schedule configuration.
    _active_warnings: List[str] = field(default_factory=list, repr=False)

    def collect_tasks(self, owner: Owner) -> List[CareTask]:
        """Retrieve every incomplete task across all of the owner's pets."""
        return [t for t in owner.all_tasks() if not t.is_completed]
    
    def sort_by_time(self, owner: Owner) -> List[CareTask]:
        """Return incomplete tasks sorted chronologically by due date and time."""
        tasks = self.collect_tasks(owner)
        return sorted(tasks, key=lambda task: (task.due_date, task.time))

    def filter_tasks(self, owner: Owner, pet_name: str = "All", completed: Optional[bool] = None) -> List[CareTask]:
        """Filter tasks dynamically by pet name and completion status."""
        tasks = owner.all_tasks()

        if pet_name != "All":
            tasks = [task for task in tasks if task.pet and task.pet.name == pet_name]

        if completed is not None:
            tasks = [task for task in tasks if task.is_completed == completed]

        return tasks

    def complete_task_and_recur(self, task: CareTask) -> Optional[CareTask]:
        """Mark a task complete and automatically schedule its next occurrence."""
        task.mark_complete()
        frequency = task.frequency.lower()

        if frequency == "daily":
            next_date = task.due_date + timedelta(days=1)
        elif frequency == "weekly":
            next_date = task.due_date + timedelta(days=7)
        elif frequency == "monthly":
            # Approximating monthly frequency safely by shifting forward 30 days
            next_date = task.due_date + timedelta(days=30)
        else:
            return None

        new_task = CareTask(
            title=task.title,
            duration=task.duration,
            frequency=task.frequency,
            priority=task.priority,
            due_date=next_date,
            time=task.time
        )

        if task.pet:
            task.pet.add_task(new_task)

        return new_task

    def check_conflicts(self, owner: Owner) -> List[str]:
        """Return lightweight warning messages if multiple tasks overlap on the same date and time."""
        tasks = owner.all_tasks()
        warnings = []
        seen_slots = {}

        for task in tasks:
            if task.is_completed:
                continue
            
            slot_key = (task.due_date, task.time)
            pet_name = task.pet.name if task.pet else "Unknown Pet"
            
            if slot_key in seen_slots:
                original_task = seen_slots[slot_key]
                orig_pet = original_task.pet.name if original_task.pet else "Unknown Pet"
                warnings.append(
                    f"⚠️ Conflict: '{task.title}' for {pet_name} overlaps with "
                    f"'{original_task.title}' for {orig_pet} at {task.time} on {task.due_date}."
                )
            else:
                seen_slots[slot_key] = task

        return warnings

    def generate_daily_schedule(self, owner: Owner, available_minutes: Optional[int] = None) -> List[CareTask]:
        """Choose and order tasks across all pets that fit the available time.

        Strategy:
            1. Run conflict verification across existing tasks.
            2. Retrieve and group all incomplete tasks from every pet.
            3. Sort tasks using multi-key priority parameters (high priority first,
               then shorter items first as a structural tie-breaker).
            4. Greedily commit tasks while remaining within the available minutes.
        """
        if available_minutes is None:
            available_minutes = owner.available_minutes

        # Refresh system conflict logs for UI warnings
        self._active_warnings = self.check_conflicts(owner)

        candidates = self.collect_tasks(owner)
        candidates.sort(key=lambda t: (-t.priority_weight, t.duration))
        self._considered = candidates

        plan: List[CareTask] = []
        remaining = available_minutes
        for task in candidates:
            if task.duration <= remaining:
                plan.append(task)
                remaining -= task.duration

        self.daily_plan = plan
        return plan

    def get_schedule_explanation(self) -> str:
        """Explain, in plain language, what made the plan, what got cut, and any structural warnings."""
        lines = []

        # 1. Print Active Conflicts/Warnings if they exist
        if self._active_warnings:
            lines.append("System Warnings:")
            for warning in self._active_warnings:
                lines.append(f"  {warning}")
            lines.append("")

        # 2. Output Active Schedule details
        if not self.daily_plan:
            lines.append("No tasks could be scheduled in the available time.")
            return "\n".join(lines)

        lines.append("Daily plan (chosen by priority, then shortest first):")
        clock = 8 * 60  # start the simulated planning timeline day at 08:00
        for task in self.daily_plan:
            start = f"{clock // 60:02d}:{clock % 60:02d}"
            who = f"{task.pet.name} — " if task.pet else ""
            lines.append(
                f"  {start}  {who}{task.title} ({task.duration} min) "
                f"[priority: {task.priority}, {task.frequency}]"
            )
            clock += task.duration

        # 3. List Dropouts / Omitted items
        planned_ids = {id(t) for t in self.daily_plan}
        cut = [t for t in self._considered if id(t) not in planned_ids]
        if cut:
            lines.append("")
            lines.append("Not scheduled (ran out of time or lower priority):")
            for task in cut:
                who = f"{task.pet.name} — " if task.pet else ""
                lines.append(f"  - {who}{task.title} ({task.duration} min) [{task.priority}]")

        return "\n".join(lines)