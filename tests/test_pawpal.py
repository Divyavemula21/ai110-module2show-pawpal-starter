"""Tests for the PawPal+ core classes.

Run from the project root with:
    pytest
"""

import os
import sys
import pytest
from datetime import date, timedelta

# Make the project root importable when pytest collects from the tests/ dir.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, CareTask, ScheduleManager


# === PHASE 2 BASE TESTS ===

def test_task_completion_changes_status():
    """Calling mark_complete() should flip is_completed from False to True."""
    task = CareTask("Morning walk", duration=30)
    assert task.is_completed is False  # tasks start incomplete

    task.mark_complete()
    assert task.is_completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet should grow that pet's task list by one."""
    pet = Pet("Mochi", "dog", age=3)
    assert len(pet.tasks) == 0  # no tasks to start

    pet.add_task(CareTask("Feeding", duration=10))
    assert len(pet.tasks) == 1


# === PHASE 4 ALGORITHMIC TESTS (PHASE 5 REQUIREMENT) ===

def test_task_sorting_chronological():
    """Verify tasks are sorted chronologically by time regardless of insertion order."""
    owner = Owner(name="Test Owner")
    pet = Pet(name="Buddy")
    owner.add_pet(pet)
    
    # Add tasks intentionally out of chronological order
    task_late = CareTask(title="Evening Feed", duration=15, time="18:00")
    task_early = CareTask(title="Morning Walk", duration=30, time="07:30")
    task_mid = CareTask(title="Midday Brush", duration=10, time="12:00")
    
    pet.add_task(task_late)
    pet.add_task(task_early)
    pet.add_task(task_mid)
    
    # Run the sorting method
    sorted_tasks = owner.schedule.sort_by_time(owner)
    
    # Assert they are arranged perfectly by time
    assert sorted_tasks[0].time == "07:30"
    assert sorted_tasks[1].time == "12:00"
    assert sorted_tasks[2].time == "18:00"


def test_recurrence_logic():
    """Confirm that marking a daily task complete creates a new task for the next day."""
    owner = Owner(name="Test Owner")
    pet = Pet(name="Luna")
    owner.add_pet(pet)
    
    initial_date = date.today()
    task = CareTask(title="Daily Meds", duration=5, frequency="daily", due_date=initial_date)
    pet.add_task(task)
    
    # Trigger completion and recurrence engine
    new_task = owner.schedule.complete_task_and_recur(task)
    
    # Assert original task is completed
    assert task.is_completed is True
    # Assert a new task was generated for tomorrow
    assert new_task is not None
    assert new_task.due_date == initial_date + timedelta(days=1)
    assert new_task.title == "Daily Meds"
    assert len(pet.tasks) == 2


def test_conflict_detection():
    """Verify that the Scheduler successfully flags duplicate times as conflicts."""
    owner = Owner(name="Test Owner")
    pet1 = Pet(name="Charlie")
    pet2 = Pet(name="Max")
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    
    # Schedule two different tasks at the exact same time slot
    task1 = CareTask(title="Charlie Feeding", duration=20, time="08:00")
    task2 = CareTask(title="Max Playtime", duration=30, time="08:00")
    
    pet1.add_task(task1)
    pet2.add_task(task2)
    
    # Pull system conflicts
    warnings = owner.schedule.check_conflicts(owner)
    
    # Assert that a warning was captured
    assert len(warnings) > 0
    assert "Conflict" in warnings[0]
    