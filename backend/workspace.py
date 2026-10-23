"""Signed anonymous browser workspaces for the hosted research library."""

import hashlib
import hmac
import re
import secrets
from contextvars import ContextVar
from http.cookies import SimpleCookie

from starlette.responses import Response, JSONResponse

workspace_id: ContextVar[str | None] = ContextVar("workspace_id", default=None)
COOKIE_NAME = "__Host-research-workspace"


class WorkspaceMiddleware:
    """Isolate report ownership without changing browser-local account signup."""

    def __init__(self, app, secret: str):
        self.app = app
        self.secret = secret.encode()

    def sign(self, identity: str) -> str:
        return hmac.new(self.secret, identity.encode(), hashlib.sha256).hexdigest()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith("/api/"):
            return await self.app(scope, receive, send)
        if len(self.secret) < 32:
            return await JSONResponse({"detail": "Hosted session configuration is missing."}, 503)(
                scope, receive, send
            )

        cookies = SimpleCookie()
        try:
            cookies.load(dict(scope.get("headers", [])).get(b"cookie", b"").decode("latin-1"))
        except Exception:
            cookies = SimpleCookie()
        entry = cookies.get(COOKIE_NAME)
        value = entry.value if entry else ""
        identity, _, signature = value.partition(".")
        valid = bool(re.fullmatch(r"[a-f0-9]{64}", identity)) and hmac.compare_digest(
            signature, self.sign(identity)
        )
        if not valid:
            identity = secrets.token_hex(32)

        async def workspace_send(message):
            if message["type"] == "http.response.start" and not valid:
                response = Response()
                response.set_cookie(
                    COOKIE_NAME,
                    f"{identity}.{self.sign(identity)}",
                    max_age=2592000,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    path="/",
                )
                message["headers"] = list(message.get("headers", [])) + [
                    (key, val) for key, val in response.raw_headers if key == b"set-cookie"
                ]
            await send(message)

        context = workspace_id.set(identity)
        try:
            await self.app(scope, receive, workspace_send)
        finally:
            workspace_id.reset(context)
