# Deployment

## Current topology

Deploy the React frontend on Vercel and the FastAPI backend on a Python host.
The backend runs a multi-step research request and saves sessions to files.
An HTTPS backend URL is required before deploying the frontend.
Localhost URLs cannot be reached from another visitor's browser.

## Backend

`render.yaml` describes the backend and an optional static frontend. You can
deploy just the backend if using Vercel for the frontend. Set `GROQ_API_KEY`
privately in the host dashboard; use `.env.example` for other settings.

Build: `pip install -r requirements.txt`

Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

Use Python 3.12. Configure a writable persistent directory through `MEMORY_DIR`
to retain report history across restarts and redeployments. Without persistent
storage, the host may discard saved reports. A persistent disk or paid plan
is optional infrastructure and is not enabled by the application.

Check `/health`, then run a real recommendation, research and PDF download.
A healthy process alone does not prove the provider key or public search works.

## Vercel frontend

1. Import the original GitHub repository.
2. Set **Root Directory** to `frontend` and framework to Vite.
3. Use `npm ci` to install, `npm run build` to build, and `dist` for output.
4. Set `VITE_API_BASE_URL` to the working backend's public HTTPS base URL.
   On the backend set `ALLOWED_ORIGINS` to the frontend's exact origin,
   e.g. `https://your-project.vercel.app` (no path or trailing slash).
   Add individual preview origins explicitly when needed; do not use a wildcard.
5. Deploy and verify recommendation → scope selection → preview → PDF download.

`frontend/vercel.json` supplies the SPA rewrite. The prebuild check rejects a
missing, insecure or localhost backend URL on Vercel. This validates the URL
shape, not backend reachability. Changing `VITE_API_BASE_URL` requires a rebuild.
Never add `GROQ_API_KEY` or any secret under a `VITE_` name: those values are
compiled into browser assets. Provider keys belong only on the backend.

Do not deploy this file-backed backend as a stateless function without adapting
session storage and request execution. Different instances may not share files.
The current backend is an anonymous college demo, not a private multi-user API.
The security update limits browser origins and local network binding. These
controls do not authorize remote API clients. Do not expose private saved
reports through this anonymous API. For a public release, complete server-side
identity, report ownership checks and request quotas before opening access.
Before opening unrestricted paid API usage, add server-side authentication,
authorization and quotas. Browser credits are presentation/demo state only.

Reference: [Vercel Vite documentation](https://vercel.com/docs/frameworks/frontend/vite).
