from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None

    def overlaps(self, other_task: "Task") -> bool:
        """Return whether this task overlaps another scheduled task."""
        if self.scheduled_start is None or self.scheduled_end is None:
            return False
        if other_task.scheduled_start is None or other_task.scheduled_end is None:
            return False

        return (
            self.scheduled_start < other_task.scheduled_end
            and other_task.scheduled_start < self.scheduled_end
        )


@dataclass
class Pet:
    name: str
    species: str
    care_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)


class Owner:
    def __init__(self, name: str, preferences: str = "") -> None:
        self.name = name
        self.preferences = preferences
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)


class Scheduler:
    def schedule_tasks(
        self,
        tasks: list[Task],
        start_time: datetime | None = None,
        available_minutes: int | None = None,
    ) -> (
        list[Task]
        | tuple[list[Task], list[Task], list[str]]
    ):
        """Schedule tasks within a time limit, or sort them for legacy callers."""
        if start_time is None and available_minutes is None:
            return self.sort_by_priority(tasks)
        if start_time is None or available_minutes is None:
            raise ValueError("Provide both start_time and available_minutes.")
        if available_minutes < 0:
            raise ValueError("available_minutes cannot be negative.")

        scheduled_tasks = []
        skipped_tasks = []
        explanations = []
        current_time = start_time
        remaining_minutes = available_minutes

        for task in self.sort_by_priority(tasks):
            task.scheduled_start = None
            task.scheduled_end = None

            if task.duration_minutes <= 0:
                skipped_tasks.append(task)
                explanations.append(
                    f"Skipped '{task.title}': duration must be greater than zero."
                )
            elif task.duration_minutes > remaining_minutes:
                skipped_tasks.append(task)
                explanations.append(
                    f"Skipped '{task.title}': it does not fit in the remaining "
                    f"{remaining_minutes} minutes."
                )
            else:
                task.scheduled_start = current_time
                task.scheduled_end = current_time + timedelta(
                    minutes=task.duration_minutes
                )
                current_time = task.scheduled_end
                remaining_minutes -= task.duration_minutes
                scheduled_tasks.append(task)
                explanations.append(
                    f"Scheduled '{task.title}' at {task.scheduled_start:%H:%M} "
                    f"because it fit in the available time."
                )

        return scheduled_tasks, skipped_tasks, explanations

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks from high to low priority."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda task: priority_order.get(task.priority.lower(), 3),
        )

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Find pairs of tasks whose scheduled times overlap."""
        conflicts = []
        for index, task in enumerate(tasks):
            for other_task in tasks[index + 1 :]:
                if task.overlaps(other_task):
                    conflicts.append((task, other_task))
        return conflicts