"""Hosted report ownership and private storage boundaries."""

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.memory.blob_store import BlobStore
from backend.workspace import COOKIE_NAME, WorkspaceMiddleware, workspace_id


def workspace_app(secret="test-signing-secret-with-at-least-32-characters"):
    app = FastAPI()

    @app.get("/api/workspace")
    async def identity():
        return {"workspace": workspace_id.get()}

    app.add_middleware(WorkspaceMiddleware, secret=secret)
    return app


@pytest.mark.asyncio
async def test_signed_cookie_keeps_workspace_and_tampering_rotates_it():
    app = workspace_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as client:
        first = await client.get("/api/workspace")
        cookie = first.headers["set-cookie"]
        assert all(flag in cookie for flag in ["HttpOnly", "Secure", "SameSite=lax", "Path=/"])
        second = await client.get("/api/workspace")
        assert first.json() == second.json()
        assert "set-cookie" not in second.headers
        client.cookies.clear()
        client.cookies.set(COOKIE_NAME, "a" * 64 + ".invalid")
        third = await client.get("/api/workspace")
        assert third.json() != first.json()
    assert workspace_id.get() is None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as other:
        assert (await other.get("/api/workspace")).json() != first.json()


@pytest.mark.asyncio
async def test_missing_hosted_signing_secret_fails_closed():
    async with AsyncClient(
        transport=ASGITransport(app=workspace_app("")), base_url="https://test"
    ) as client:
        response = await client.get("/api/workspace")
        assert response.status_code == 503
        assert "set-cookie" not in response.headers


def test_private_blob_storage_uses_workspace_namespace():
    store = BlobStore("a" * 64)
    other = BlobStore("b" * 64)
    assert store.path("report-1") != other.path("report-1")
    for invalid in ["../report", "", "x" * 129]:
        with pytest.raises(ValueError):
            store.path(invalid)
    with pytest.raises(ValueError):
        BlobStore(None)
    with patch("backend.memory.blob_store.sync.put_blob") as upload:
        store.save("report-1", {"summary": "Saved research"})
        assert upload.call_args.kwargs["access"] == "private"
        assert upload.call_args.args[0] == store.path("report-1")
        assert json.loads(upload.call_args.args[1])["summary"] == "Saved research"
    with patch(
        "backend.memory.blob_store.sync.get_blob",
        return_value=SimpleNamespace(body=b'{"summary":"Saved"}'),
    ) as download:
        assert store.load("report-1")["summary"] == "Saved"
        download.assert_called_once_with(store.path("report-1"), access="private")
    with patch(
        "backend.memory.blob_store.sync.get_blob", side_effect=RuntimeError("Storage unavailable")
    ):
        with pytest.raises(RuntimeError):
            store.load("report-1")
