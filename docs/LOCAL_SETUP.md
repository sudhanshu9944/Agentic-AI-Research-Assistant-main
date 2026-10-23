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
