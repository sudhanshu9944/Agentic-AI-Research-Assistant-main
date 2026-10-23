# Research.AI

A research workspace where you choose the scope, inspect source-based findings, and generate a PDF when ready. Built with React, FastAPI, LangGraph and Groq.

![Light theme](docs/screenshots/workspace-light.png)

<details>
<summary>Dark theme and research preview</summary>

![Dark theme](docs/screenshots/workspace-dark.png)
![Research preview](docs/screenshots/research-preview.png)

</details>

## Start here

- [Local installation and daily use](docs/LOCAL_SETUP.md)
- [API keys and configuration](docs/CONFIGURATION.md)
- [Architecture and code map](docs/ARCHITECTURE.md)
- [API reference](docs/API.md)
- [Vercel frontend and backend deployment](docs/DEPLOYMENT.md)
- [Verification and known limits](docs/VERIFICATION.md)
- [Development conventions](CONTRIBUTING.md)

## Run locally on Windows

Install Python 3.12 and Node.js 24 LTS. Extract the ZIP, then open a terminal in the project root:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Open `.env` and fill in `GROQ_API_KEY`. Keep it private; do not overwrite an existing configured `.env`.

Start the backend:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open a second terminal in the project root:

```powershell
cd frontend
npm ci
npm run dev
```

Open **http://127.0.0.1:5173** and keep both terminals running. No Python activation or execution-policy change is needed. See the local guide for macOS/Linux, preview mode and troubleshooting.

## Research flow

1. Sign up locally for 100 demo app tokens, or log in to this browser's account.
2. Enter a topic. AI suggests relevant angles for 2 app tokens.
3. Select the checkboxes you want; add your own angle if needed.
4. Research the chosen scope for 10 app tokens.
5. Read the summary, excluded topics and evidence gaps; inspect sources and the full report.
6. Generate a PDF or Markdown file for free. Failed operations refund their reserved app tokens.

Theme selection and local login persist in the browser. Public links and footer credits are centralized in `frontend/src/config/project.js`.

## Repository layout

```text
backend/
  api/routes/        Health, research, history and export endpoints
  agents/            Planning, research, analysis, summary and reporting
  services/          Provider calls, retry budgets and relevance ranking
  tools/             Search adapters
  graph/             Workflow composition and persistence handoff
  schemas/           API and workflow-state contracts
  memory/            Atomic JSON session storage
  export/            PDF/Markdown rendering, fonts and licenses
frontend/
  src/app/           App composition and workspace orchestration
  src/features/      Research views, local accounts and theme behavior
  src/components/    Shared layout and notifications
  src/services/      HTTP client and explicit file downloads
  src/config/        Public project links and credits
  src/styles/        Readable styles grouped by responsibility
  tests/             Account/token-ledger behavior tests
  scripts/           Deployment configuration validation
tests/               Backend API, workflow, storage and export tests
docs/                Setup, architecture, configuration and deployment
.github/workflows/   Automated quality checks
```

## Development checks

```powershell
.venv\Scripts\python.exe -m ruff check backend tests
.venv\Scripts\python.exe -m ruff format --check backend tests
.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run format:check
npm run lint
npm test
npm run build
```

## Boundaries

Local accounts and app tokens live in browser localStorage. They are demonstration controls, not server authentication or secure billing. The saved research library belongs to the installation. Groq's actual quota is separate.

Research uses retrieved search excerpts, not complete article/PDF ingestion or uploaded-PDF OCR. Public search and free API availability vary. Essential failures produce errors rather than fabricated successful reports.

The source package excludes API keys, account passwords, generated reports, history, virtual environments and node_modules. See [credits](CREDITS.md) and the bundled [font license](backend/export/fonts/LICENSE).

Made with ❤️ by **Sudhanshu Singh, Himanshu Chauhan, Tanmay Pahuja**.

*Built with ❤️ using* React · FastAPI · LangGraph · Groq.
