"""Compose route modules; application setup imports only this router."""

from fastapi import APIRouter
from backend.api.routes import health, research, history, exports

router = APIRouter()
for module in (health, research, history, exports):
    router.include_router(module.router)
