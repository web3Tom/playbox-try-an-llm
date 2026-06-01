"""Application entrypoint — wires the API routes to a running server."""

from api.routes import build_router


def create_app():
    """Construct the application and register its routes."""
    router = build_router()
    return router


def main():
    app = create_app()
    print("Todo API ready with routes:", app.list_routes())


if __name__ == "__main__":
    main()
