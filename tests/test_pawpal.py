"""Tests for the PawPal+ core classes.

Run from the project root with:
    pytest
"""

import os
import sys

# Make the project root importable when pytest collects from the tests/ dir.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Pet, CareTask


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
