"""API layer — maps HTTP-ish routes to service calls."""

from services.todo_service import TodoService


class Router:
    def __init__(self, service):
        self.service = service
        self.routes = {
            "GET /todos": self.service.list_todos,
            "POST /todos": self.service.add_todo,
            "DELETE /todos": self.service.remove_todo,
        }

    def list_routes(self):
        return list(self.routes.keys())


def build_router():
    """Create the router with a wired-up service."""
    return Router(TodoService())
