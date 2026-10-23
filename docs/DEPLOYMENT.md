# Deployment

## Vercel: frontend and API together

Import the repository into the **sudhanshu singh** Vercel team. Use the repository
root (`./`) and the **FastAPI** preset. The root `vercel.json` and `pyproject.toml`
select `backend.main:app`; the build script installs and builds the React app.
Do not select the inferred Services preset or set the root to `frontend` for
this deployment.

The browser calls `/api` on the same origin. Static frontend assets are served
through the Vercel CDN; research and exports run in the Python function, with a
300-second maximum duration. Keep Python 3.12. Provider/search limits and the
hosting plan still apply; a timeout does not guarantee an upstream request stopped.

### Environment

Set these in the project's private environment settings, never in Git:

| Variable | Value |
| --- | --- |
| `GROQ_API_KEY` | Your provider key |
| `SESSION_SECRET` | At least 32 random characters; keep stable across deployments |
| `DEFAULT_MODEL` | `openai/gpt-oss-120b` |
| `RERANKER_MODEL` | `openai/gpt-oss-20b` |
| `OPENROUTER_BASE_URL` | `https://api.groq.com/openai/v1` |

Create a **private Vercel Blob store** and connect it to this project for the
chosen deployment environments. Use the credentials/store identifier supplied
by that connection; do not put a Blob token in frontend variables. The official
Python SDK supports the connected store's OIDC configuration or its private
`BLOB_READ_WRITE_TOKEN`. No browser receives these credentials.

The build supplies `VITE_API_BASE_URL=/api`. Automatic deployment and production
hostnames are accepted as browser origins. If adding a custom domain, add its
exact HTTPS origin to `ALLOWED_ORIGINS`; do not use a wildcard. Redeploy after
changing environment variables or connecting storage.

### Report ownership

A signed, Secure, HttpOnly browser cookie identifies an anonymous workspace.
Reports are saved under that workspace's private Blob prefix, and API history,
report retrieval and exports use that prefix. Other browser workspaces cannot
retrieve a report simply by guessing its report ID. Clearing the cookie loses
access to that browser library; rotating `SESSION_SECRET` invalidates existing
workspace cookies. Browser-local accounts do not sync this library across devices.

Local accounts and demo credits remain client state, not API authentication or
a server-enforced spending limit. Public callers can create anonymous workspaces
and consume provider quota. Use free-provider limits for a college demonstration;
add server authentication and abuse controls before offering paid or unrestricted
public usage. Avoid storing confidential research in this demonstration.

### Release checks

Check `/api/health`, then complete recommendations → chosen outline → research
preview → PDF and Markdown downloads. Refresh history and verify that a different
browser workspace cannot retrieve the saved report. Check function logs for
storage, provider or search failures. Health alone does not test these services.

## Local or separate Python hosting

Local development stays unchanged: run FastAPI on port 8000 and Vite separately.
With `VERCEL` unset, sessions use atomic JSON files under `MEMORY_DIR` and the API
has no `/api` prefix. This local library is shared within that installation.

`render.yaml` remains available for a separate Python host. Use Python 3.12,
`pip install -r requirements.txt`, and
`uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. Configure persistent storage
for `MEMORY_DIR` if history must survive redeployments. For a separate Vite frontend,
use `frontend` as its root and set `VITE_API_BASE_URL` to that backend's public
HTTPS URL; add the frontend's exact origin to backend `ALLOWED_ORIGINS`.

References: [FastAPI on Vercel](https://vercel.com/docs/frameworks/backend/fastapi),
[Blob Python SDK](https://vercel.com/docs/vercel-blob/python-sdk-reference).
