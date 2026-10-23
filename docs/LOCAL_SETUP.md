# Local setup

## Requirements

- Python 3.12 and Node.js 24 LTS (with npm).
- Internet access for installation, public search, fonts and the AI provider.
- A Groq API key in the project-root `.env` file.

Extract the ZIP first. Open a terminal in the folder containing `README.md`, `backend` and `frontend`.

## First installation on Windows

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

If `py` is unavailable but `python --version` shows Python 3.12, use `python -m venv .venv`. Do not copy the example over an existing `.env` containing your key.

Open `.env` in a text editor and fill in the value after `GROQ_API_KEY=`. Keep the key private. It belongs on the backend, never in frontend source or a `VITE_` variable.

Install frontend dependencies once:

```powershell
cd frontend
npm ci
```

## Start the app each day

Terminal 1, from the project root:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Terminal 2, from the project root:

```powershell
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173**. Keep both terminals running. Stop each with Ctrl+C. No Python environment activation or PowerShell execution-policy change is required.

For a production-build preview, leave the backend running and use:

```powershell
cd frontend
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

Then open http://127.0.0.1:4173. Installing dependencies is a first-time step, not a daily step.

## macOS / Linux

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
# Edit .env before starting the backend.
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

## Change the API key

1. Open the root `.env`, beside `README.md`.
2. Replace the value after `GROQ_API_KEY=` with the new key.
3. Save, then stop and restart the backend terminal.
4. Run a real topic to confirm provider access. A frontend rebuild is unnecessary for this change.

`http://127.0.0.1:8000/health` should show `healthy`. `research_ready` only means a key is present; it does not validate the key with Groq. API documentation is at `/docs`.

## Troubleshooting

| Problem | Check |
|---|---|
| Backend unavailable | Start terminal 1 on port 8000 and keep it open. |
| Key still missing | Check that the filename is `.env`, not `.env.txt`, and restart the backend. |
| Model unavailable | Check the model IDs, provider URL and account access. |
| API cooldown | Allow the request to retry. Failed operations refund their reserved app tokens. |
| No usable search results | Public search may be throttled or unavailable. Retry later or use a specific topic. |
| Old UI in preview | Rebuild with `npm run build`, then refresh. |
| Port already in use | Stop the old copy before starting another. |
| Local account disappeared | Browser accounts are specific to browser and origin. Clearing storage removes them; ports 5173 and 4173 have separate storage. |

Saved reports live in `memory/`. Back up that folder if moving research to another installation; do not publish private reports with the source.


## Configuration reference

Backend settings are read from the root `.env` when the server starts.

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Provider key. Never put it in frontend code. |
| `OPENROUTER_API_KEY` | Legacy key alias; used when `GROQ_API_KEY` is absent. |
| `OPENROUTER_BASE_URL` | Provider base URL; defaults to Groq's OpenAI-compatible endpoint. |
| `DEFAULT_MODEL` / `RERANKER_MODEL` | Research and relevance-ranking model IDs. |
| `GROQ_TOKEN_BUDGET` | Request/completion budgeting; default 8000. |
| `BACKEND_HOST` / `BACKEND_PORT` | Local bind address and port; defaults 127.0.0.1:8000. |
| `ALLOWED_ORIGINS` | Exact comma-separated frontend origins; local ports 5173, 4173 and 80 are allowed by default. |
| `MEMORY_DIR` / `REPORTS_DIR` | Writable session and file-export directories. |
| `DEBUG` | Additional development logs; defaults false. |

Leave frontend `VITE_API_BASE_URL` unset locally to use the `/api` proxy.
On a static host, set it to the public HTTPS backend URL and rebuild.
This setting is public; never place credentials in a `VITE_` variable.

Repository links and credits are in `frontend/src/config/project.js`.
Model choices are in `frontend/src/features/research/config.js`; demo token
prices are in `frontend/src/features/account/services/localAccounts.js`.

## Change the model or provider

For the same Groq provider, replace only `GROQ_API_KEY` in the root `.env` and
restart the backend. For a different OpenAI-compatible provider, also change
`OPENROUTER_BASE_URL`, `DEFAULT_MODEL` and `RERANKER_MODEL` to values it supports.
The model selected in the browser is sent in each request: update `MODELS` in
`frontend/src/features/research/config.js` if adding/removing provider models.
Never put the provider key in that frontend file.

On Vercel, change keys through the project's **Settings → Environment Variables**
and redeploy. The hosted UI and API run together; local development needs neither
Blob credentials nor SESSION_SECRET. Leave VERCEL unset on your computer.

Live demo: https://agentic-ai-research-assistant-main.vercel.app/
