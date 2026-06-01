"""Data/persistence layer — an in-memory repository for Todo entities."""

from models.todo import Todo


class TodoRepository:
    def __init__(self):
        self._items: dict[int, Todo] = {}
        self._counter = 0

    def next_id(self) -> int:
        self._counter += 1
        return self._counter

    def all(self) -> list[Todo]:
        return list(self._items.values())

    def save(self, todo: Todo) -> None:
        self._items[todo.id] = todo

    def delete(self, todo_id: int) -> bool:
        return self._items.pop(todo_id, None) is not None
