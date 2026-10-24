"""A tiny in-memory task store used as a FixBot demo.

This file intentionally contains a few seeded bugs. Each one is described
in a GitHub issue, and the test suite in tests/ defines the correct behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TaskNotFound(Exception):
    """Raised when a task id does not exist."""


class TaskStore:
    def __init__(self) -> None:
        self._open: dict[int, Task] = {}
        self._done: dict[int, Task] = {}
        self._ids = count(1)

    # --- create -----------------------------------------------------------
    def add(self, title: str, tags: list[str] | None = None) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("title must not be empty")
        task = Task(id=next(self._ids), title=title, tags=list(tags or []))
        self._open[task.id] = task
        return task

    # --- read -------------------------------------------------------------
    def get(self, task_id: int) -> Task:
        task = self._open.get(task_id) or self._done.get(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def all(self) -> list[Task]:
        tasks = [*self._open.values(), *self._done.values()]
        return sorted(tasks, key=lambda t: t.id)

    def paginate(self, page: int = 1, per_page: int = 10) -> list[Task]:
        """Return one page of tasks (pages start at 1)."""
        if page < 1 or per_page < 1:
            raise ValueError("page and per_page must be >= 1")
        tasks = self.all()
        start = (page - 1) * per_page
        end = start + per_page
        return tasks[start : end - 1]

    def search(self, query: str) -> list[Task]:
        """Find tasks whose title contains the query."""
        return [t for t in self.all() if query in t.title]

    # --- update -----------------------------------------------------------
    def complete(self, task_id: int) -> Task:
        task = self._open.pop(task_id, None)
        if task is None:
            raise TaskNotFound(task_id)
        task.done = True
        self._done[task.id] = task
        return task

    # --- delete -----------------------------------------------------------
    def delete(self, task_id: int) -> None:
        if task_id not in self._open:
            raise TaskNotFound(task_id)
        del self._open[task_id]
