"""Business-logic layer — todo operations, independent of storage or transport."""

from models.todo import Todo
from storage.repository import TodoRepository


class TodoService:
    def __init__(self):
        self.repo = TodoRepository()

    def list_todos(self):
        return self.repo.all()

    def add_todo(self, title):
        todo = Todo(id=self.repo.next_id(), title=title, done=False)
        self.repo.save(todo)
        return todo

    def remove_todo(self, todo_id):
        return self.repo.delete(todo_id)
