from dataclasses import dataclass, field
from datetime import datetime


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
    def schedule_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks in priority order as a starting point for a schedule."""
        return self.sort_by_priority(tasks)

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