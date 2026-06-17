import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from backend.app import app as backend_app  # noqa: E402


class ApiPrefixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in {"http", "websocket"} and scope["path"].startswith("/api"):
            scope = dict(scope)
            scope["path"] = scope["path"][4:] or "/"
            scope["root_path"] = f"{scope.get('root_path', '')}/api"
        await self.app(scope, receive, send)


app = ApiPrefixMiddleware(backend_app)
