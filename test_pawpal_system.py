from datetime import datetime

import pytest

from pawpal_system import Scheduler, Task


def make_task(title: str, duration: int, priority: str) -> Task:
    return Task(title=title, duration_minutes=duration, priority=priority)


def test_tasks_are_sorted_by_priority():
    scheduler = Scheduler()
    tasks = [
        make_task("Grooming", 20, "low"),
        make_task("Walk", 30, "high"),
        make_task("Feeding", 10, "medium"),
    ]

    scheduled, skipped, _ = scheduler.schedule_tasks(
        tasks, datetime(2026, 10, 18, 8, 0), 60
    )

    assert [task.title for task in scheduled] == ["Walk", "Feeding", "Grooming"]
    assert skipped == []


def test_tasks_receive_correct_start_and_end_times():
    scheduler = Scheduler()
    tasks = [make_task("Walk", 30, "high"), make_task("Feeding", 10, "medium")]

    scheduled, _, _ = scheduler.schedule_tasks(
        tasks, datetime(2026, 10, 18, 8, 0), 45
    )

    assert (scheduled[0].scheduled_start, scheduled[0].scheduled_end) == (
        datetime(2026, 10, 18, 8, 0),
        datetime(2026, 10, 18, 8, 30),
    )
    assert (scheduled[1].scheduled_start, scheduled[1].scheduled_end) == (
        datetime(2026, 10, 18, 8, 30),
        datetime(2026, 10, 18, 8, 40),
    )


def test_tasks_that_do_not_fit_are_skipped_and_explained():
    scheduler = Scheduler()
    tasks = [
        make_task("Long walk", 40, "high"),
        make_task("Feeding", 20, "medium"),
        make_task("Brush", 10, "low"),
    ]

    scheduled, skipped, explanations = scheduler.schedule_tasks(
        tasks, datetime(2026, 10, 18, 8, 0), 35
    )

    assert [task.title for task in skipped] == ["Long walk"]
    assert [task.title for task in scheduled] == ["Feeding", "Brush"]
    assert any("Long walk" in reason and "Skipped" in reason for reason in explanations)


def test_scheduled_tasks_do_not_overlap():
    scheduler = Scheduler()
    tasks = [
        make_task("Walk", 30, "high"),
        make_task("Feeding", 10, "medium"),
        make_task("Play", 15, "low"),
    ]

    scheduled, _, _ = scheduler.schedule_tasks(
        tasks, datetime(2026, 10, 18, 8, 0), 60
    )

    assert scheduler.detect_conflicts(scheduled) == []
    for current_task, next_task in zip(scheduled, scheduled[1:]):
        assert current_task.scheduled_end <= next_task.scheduled_start


@pytest.mark.parametrize("duration", [0, -5])
def test_invalid_durations_are_skipped(duration: int):
    scheduler = Scheduler()
    task = make_task("Invalid task", duration, "high")

    scheduled, skipped, explanations = scheduler.schedule_tasks(
        [task], datetime(2026, 10, 18, 8, 0), 30
    )

    assert scheduled == []
    assert skipped == [task]
    assert task.scheduled_start is None
    assert task.scheduled_end is None
    assert "duration must be greater than zero" in explanations[0]


def test_one_argument_call_still_returns_priority_sorted_list():
    scheduler = Scheduler()
    tasks = [
        make_task("Brush", 10, "low"),
        make_task("Walk", 30, "high"),
        make_task("Feeding", 10, "medium"),
    ]

    result = scheduler.schedule_tasks(tasks)

    assert isinstance(result, list)
    assert [task.title for task in result] == ["Walk", "Feeding", "Brush"]
    assert all(task.scheduled_start is None for task in tasks)
    assert all(task.scheduled_end is None for task in tasks)