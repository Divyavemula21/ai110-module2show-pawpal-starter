"""PawPal+ command-line demo.

Builds a small sample household (one owner, two pets, several care tasks)
and prints today's schedule to the terminal. Run with:

    python main.py
"""

from pawpal_system import Owner, Pet, CareTask


def build_demo() -> Owner:
    """Create a sample owner with two pets and a handful of care tasks."""
    owner = Owner("Jordan", available_hours=1.5)  # 90 minutes available today

    # Pet 1: a dog with morning-care tasks.
    mochi = Pet("Mochi", "dog", age=3)
    mochi.add_task(CareTask("Morning walk", duration=30, frequency="daily", priority="high"))
    mochi.add_task(CareTask("Grooming", duration=45, frequency="weekly", priority="low"))

    # Pet 2: a cat with shorter, frequent tasks.
    biscuit = Pet("Biscuit", "cat", age=5)
    biscuit.add_task(CareTask("Feeding", duration=10, frequency="daily", priority="high"))
    biscuit.add_task(CareTask("Litter clean", duration=15, frequency="daily", priority="medium"))

    owner.add_pet(mochi)
    owner.add_pet(biscuit)
    return owner


def main() -> None:
    owner = build_demo()

    print(f"Owner: {owner.name}  (available today: {owner.available_minutes} min)")
    print("Pets:")
    for pet in owner.pets:
        print(f"  - {pet.get_profile_summary()}  [{len(pet.tasks)} task(s)]")

    print("\n" + "=" * 48)
    print("Today's Schedule")
    print("=" * 48)

    owner.schedule.generate_daily_schedule(owner)
    print(owner.schedule.get_schedule_explanation())


if __name__ == "__main__":
    main()
