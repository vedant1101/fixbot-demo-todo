import pytest

from todo.store import TaskNotFound, TaskStore


@pytest.fixture
def store() -> TaskStore:
    return TaskStore()


def test_add_assigns_incrementing_ids(store):
    a = store.add("Write README")
    b = store.add("Ship v1")
    assert (a.id, b.id) == (1, 2)


def test_add_strips_title(store):
    assert store.add("  Buy milk  ").title == "Buy milk"


def test_add_rejects_empty_title(store):
    with pytest.raises(ValueError):
        store.add("   ")


def test_get_missing_task_raises(store):
    with pytest.raises(TaskNotFound):
        store.get(42)


def test_complete_marks_task_done(store):
    task = store.add("Pay rent")
    store.complete(task.id)
    assert store.get(task.id).done is True


# --- pagination (issue #1) ---
def test_paginate_returns_full_page(store):
    for i in range(5):
        store.add(f"Task {i}")
    assert [t.title for t in store.paginate(page=1, per_page=2)] == ["Task 0", "Task 1"]


def test_paginate_last_page_includes_last_item(store):
    for i in range(5):
        store.add(f"Task {i}")
    assert [t.title for t in store.paginate(page=3, per_page=2)] == ["Task 4"]


def test_paginate_rejects_bad_input(store):
    with pytest.raises(ValueError):
        store.paginate(page=0)


# --- delete (issue #2) ---
def test_delete_open_task(store):
    task = store.add("Temp")
    store.delete(task.id)
    with pytest.raises(TaskNotFound):
        store.get(task.id)


def test_delete_completed_task(store):
    task = store.add("Done already")
    store.complete(task.id)
    store.delete(task.id)
    with pytest.raises(TaskNotFound):
        store.get(task.id)


def test_delete_missing_task_raises(store):
    with pytest.raises(TaskNotFound):
        store.delete(99)


# --- search (issue #3) ---
def test_search_matches_substring(store):
    store.add("Buy milk")
    store.add("Walk dog")
    assert [t.title for t in store.search("milk")] == ["Buy milk"]


def test_search_is_case_insensitive(store):
    store.add("Buy Milk")
    store.add("Walk dog")
    assert [t.title for t in store.search("milk")] == ["Buy Milk"]
    assert [t.title for t in store.search("WALK")] == ["Walk dog"]
