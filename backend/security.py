"""Local browser isolation, bounded request bodies and safe external links."""

from __future__ import annotations

import logging
import os
import re
from urllib.parse import urlsplit

from starlette.responses import JSONResponse


class RedactingFormatter(logging.Formatter):
    """Remove configured keys and common credential formats, including tracebacks."""

    def format(self, record):
        from backend.config import settings

        message = super().format(record)
        for secret in (
            settings.OPENROUTER_API_KEY,
            settings.SESSION_SECRET,
            os.getenv("BLOB_READ_WRITE_TOKEN", ""),
        ):
            if secret:
                message = message.replace(secret, "[REDACTED]")
        return re.sub(
            r"\b(?:gsk_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|"
            r"gh[pousr]_[A-Za-z0-9]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{30,})",
            "[REDACTED]",
            message,
        )


def safe_external_url(value: str) -> str | None:
    """Keep web citations; never create executable, file or credential-bearing links."""
    if not isinstance(value, str) or any(ord(char) < 33 for char in value) or "\\" in value:
        return None
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme.lower() in {"http", "https"}
            and parsed.hostname
            and not parsed.username
            and not parsed.password
        ):
            return value
    except ValueError:
        pass
    return None


class BrowserBoundaryMiddleware:
    """Reject unapproved browser origins before work and cap incoming JSON at 32 KiB.

    Origin checking protects local use from unrelated websites. It is not server
    authentication: non-browser clients can omit or forge Origin.
    """

    def __init__(self, app, allowed_origins: list[str], max_body: int = 32768):
        self.app = app
        self.allowed_origins = set(allowed_origins)
        self.max_body = max_body

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        headers = dict(scope.get("headers", []))
        origin = headers.get(b"origin")
        if origin is not None and origin.decode("latin-1") not in self.allowed_origins:
            return await JSONResponse({"detail": "Browser origin is not allowed."}, 403)(
                scope, receive, send
            )

        messages = []
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > self.max_body:
                return await JSONResponse({"detail": "Request body is too large."}, 413)(
                    scope, receive, send
                )
            messages.append(message)
            if not message.get("more_body", False):
                break

        async def bounded_receive():
            return messages.pop(0) if messages else await receive()

        async def secure_send(message):
            if message["type"] == "http.response.start":
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"cache-control", b"no-store"),
                ]
            await send(message)

        await self.app(scope, bounded_receive, secure_send)
