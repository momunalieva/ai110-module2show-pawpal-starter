from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", preferences="Morning care before work")
    pet = Pet(name="Biscuit", species="Golden Retriever")
    owner.add_pet(pet)

    tasks = [
        Task("Morning walk", 30, "high"),
        Task("Breakfast", 10, "high"),
        Task("Give medication", 5, "medium"),
        Task("Play and enrichment", 25, "medium"),
        Task("Brush coat", 10, "low"),
    ]
    for task in tasks:
        pet.add_task(task)
        owner.add_task(task)

    start_time = datetime(2026, 10, 18, 8, 0)
    available_minutes = 60
    scheduled, skipped, explanations = Scheduler().schedule_tasks(
        pet.tasks,
        start_time=start_time,
        available_minutes=available_minutes,
    )

    print(f"Daily plan for {pet.name} ({pet.species})")
    print(f"Owner: {owner.name}")
    print(f"Available time: {start_time:%H:%M} for {available_minutes} minutes")

    print("\nScheduled tasks:")
    if scheduled:
        for task in scheduled:
            print(
                f"  {task.scheduled_start:%H:%M}-{task.scheduled_end:%H:%M}"
                f" - {task.title} ({task.duration_minutes} min,"
                f" priority: {task.priority})"
            )
    else:
        print("  None")

    print("\nSkipped tasks:")
    if skipped:
        for task in skipped:
            print(f"  {task.title} ({task.duration_minutes} min)")
    else:
        print("  None")

    print("\nDecisions:")
    for explanation in explanations:
        print(f"  - {explanation}")


if __name__ == "__main__":
    main()