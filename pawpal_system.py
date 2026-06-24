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

# Priority labels mapped to a sort weight (higher = more important).
PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


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
    # Back-reference to the pet this task belongs to. Set by Pet.add_task().
    # repr/compare excluded to avoid Pet<->CareTask recursion and identity surprises.
    pet: "Pet" = field(default=None, repr=False, compare=False)

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
    tasks: list = field(default_factory=list)   # list[CareTask]

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
    pets: list = field(default_factory=list)              # list[Pet]
    schedule: "ScheduleManager" = None                    # set in __post_init__

    def __post_init__(self) -> None:
        """Give the owner their own scheduler if one wasn't supplied."""
        # Done here (not as a default factory) so ScheduleManager only needs
        # to exist at instantiation time.
        if self.schedule is None:
            self.schedule = ScheduleManager()

    def add_pet(self, pet: Pet) -> None:
        """Register a pet this owner cares for."""
        self.pets.append(pet)

    def all_tasks(self) -> list:
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

    daily_plan: list = field(default_factory=list)          # list[CareTask]
    # Incomplete tasks considered in the most recent run (for the explanation).
    _considered: list = field(default_factory=list, repr=False)

    def collect_tasks(self, owner: Owner) -> list:
        """Retrieve every incomplete task across all of the owner's pets."""
        return [t for t in owner.all_tasks() if not t.is_completed]

    def generate_daily_schedule(self, owner: Owner, available_minutes: int = None) -> list:
        """Choose and order tasks across all pets that fit the available time.

        Strategy:
            1. Retrieve all incomplete tasks from every pet.
            2. Sort by priority (high first), then shorter tasks first as a
               tie-breaker so we can fit more high-value tasks.
            3. Greedily add tasks while they fit in the remaining time.
        Stores and returns the resulting plan.
        """
        if available_minutes is None:
            available_minutes = owner.available_minutes

        candidates = self.collect_tasks(owner)
        candidates.sort(key=lambda t: (-t.priority_weight, t.duration))
        self._considered = candidates

        plan: list = []
        remaining = available_minutes
        for task in candidates:
            if task.duration <= remaining:
                plan.append(task)
                remaining -= task.duration

        self.daily_plan = plan
        return plan

    def get_schedule_explanation(self) -> str:
        """Explain, in plain language, what made the plan and what got cut."""
        if not self.daily_plan:
            return "No tasks could be scheduled in the available time."

        lines = ["Daily plan (chosen by priority, then shortest first):"]
        clock = 8 * 60  # start the day at 08:00, in minutes since midnight
        for task in self.daily_plan:
            start = f"{clock // 60:02d}:{clock % 60:02d}"
            who = f"{task.pet.name} — " if task.pet else ""
            lines.append(
                f"  {start}  {who}{task.title} ({task.duration} min) "
                f"[priority: {task.priority}, {task.frequency}]"
            )
            clock += task.duration

        planned_ids = {id(t) for t in self.daily_plan}
        cut = [t for t in self._considered if id(t) not in planned_ids]
        if cut:
            lines.append("")
            lines.append("Not scheduled (ran out of time or lower priority):")
            for task in cut:
                who = f"{task.pet.name} — " if task.pet else ""
                lines.append(f"  - {who}{task.title} ({task.duration} min) [{task.priority}]")

        return "\n".join(lines)
