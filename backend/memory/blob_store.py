"""Private Vercel Blob storage; each signed workspace owns a separate prefix."""

import json
import re
from datetime import datetime, timezone

from vercel.blob import BlobNotFoundError, sync


class BlobStore:
    def __init__(self, workspace: str | None):
        if not workspace or not re.fullmatch(r"[a-f0-9]{64}", workspace):
            raise ValueError("A signed workspace is required for hosted storage.")
        self.prefix = f"workspaces/{workspace}/reports/"

    def path(self, session_id: str) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", session_id):
            raise ValueError("Invalid session ID")
        return f"{self.prefix}{session_id}.json"

    def save(self, session_id: str, data: dict) -> None:
        sync.put_blob(
            self.path(session_id),
            json.dumps(data, ensure_ascii=False, default=str).encode(),
            access="private",
            content_type="application/json",
            allow_overwrite=True,
            cache_control_max_age=60,
        )

    def load(self, session_id: str) -> dict | None:
        try:
            data = json.loads(sync.get_blob(self.path(session_id), access="private").body)
        except BlobNotFoundError:
            return None
        return data

    def list(self) -> list[dict]:
        items = sorted(
            sync.query_blobs(prefix=self.prefix), key=lambda item: item.uploaded_at, reverse=True
        )[:100]
        sessions = []
        for item in items:
            session_id = item.pathname.removeprefix(self.prefix).removesuffix(".json")
            data = self.load(session_id)
            if data:
                sessions.append(
                    {
                        "session_id": session_id,
                        "query": data.get("user_query", "Unknown"),
                        "created_at": data.get(
                            "created_at", datetime.now(timezone.utc).isoformat()
                        ),
                        "summary_preview": data.get("summary", "")[:200],
                    }
                )
        return sessions

    def delete(self, session_id: str) -> bool:
        if self.load(session_id) is None:
            return False
        sync.delete_blob(self.path(session_id))
        return True
