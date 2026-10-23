"""Safe Content-Disposition headers shared by export endpoints."""

from urllib.parse import quote


def download_header(query: str, extension: str) -> str:
    """HTTP headers must be Latin-1; carry the real title using RFC 5987."""
    name = (
        "".join(c if c.isalnum() or c in " -_" else "_" for c in query[:40]).strip() or "research"
    )
    fallback = name.encode("ascii", "ignore").decode().strip() or "research"
    return f"attachment; filename=\"{fallback}_report.{extension}\"; filename*=UTF-8''{quote(name + '_report.' + extension)}"
